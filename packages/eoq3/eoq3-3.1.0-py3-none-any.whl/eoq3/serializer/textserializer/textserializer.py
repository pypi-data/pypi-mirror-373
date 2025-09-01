'''
 Bjoern Annighoefer 2022
'''


from .eoq3Lexer import eoq3Lexer
from .eoq3Listener import eoq3Listener
from .eoq3Parser import eoq3Parser

from ..serializer import Serializer, RegisterSerializer
 
from ...frame import Frm
from ...value import VAL, BOL, U32, U64, I32, I64, F32, F64, STR, DAT, NON, QRY, LST, ValCompare
from ...query import Qry, Seg
from ...command import Cmd, Cmp, CmdFactory, GetCmdInfo, PrmCmd
from ...error import EOQ_ERROR_INVALID_VALUE, EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_RUNTIME

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener

import re

from typing import List, Any


#define a list of symbols for the textual representation
QRY_SYMBOLS = {
    'OBJ' : '#',
    'ONI' : '`', 
    'HIS' : '$', 
    'PTH' : '/', 
    'CLS' : '!', 
    'INO' : '?',
    'MET' : '@',
    'NOT' : '&NOT',
    'TRM' : '&TRM',
    'TRY' : '&TRY',
    'QRF' : '&QRF',
    'STF' : '&STF',
    'SLF' : '&SLF',
    'IDX' : ':', 
    'SEL' : '{', 
    'ARR' : '&ARR', 
    'ZIP' : '&ZIP',
    'ANY' : '&ANY',
    'ALL' : '&ALL', 
    'EQU' : '=',
    'EQA' : '&EQA',
    'NEQ' : '~', 
    'LES' : '<', 
    'GRE' : '>',
    'RGX' : '&RGX',
    'ADD' : '&ADD', 
    'SUB' : '&SUB', 
    'MUL' : '&MUL', 
    'DIV' : '&DIV', 
    'ORR' : '&ORR', 
    'XOR' : '&XOR', 
    'AND' : '&AND', 
    'NAD' : '&NAD', 
    'CSP' : '&CSP', 
    'ITS' : '&ITS', 
    'DIF' : '\\',
    'UNI' : '&UNI', 
    'CON' : '|'
}  
#free symbols: `´
#reserved symbols: *{}()[]'"+-.,

# special commands for handling single and no command cmp commands
CMD_TYPE_PDD = 'PDD' #pseudo padding command type
class Pdd(PrmCmd):
    def __init__(self):
        super().__init__(CMD_TYPE_PDD, [],True,None)

# create a look up table for single char query symbols
QRY_SYMBOLS_LOT = {} #contains query char->3 letter encoding
for k,v in QRY_SYMBOLS.items(): 
    if('&' != v[0]):
        QRY_SYMBOLS_LOT[v] = k

STR_SIMPLE_1 = "[A-Za-z0-9+\\-*_]*[A-Za-z+\\-*._]" # copied from .g4 file
STR_SIMPLE_2 = "[A-Za-z0-9+\\-*_][A-Za-z*._][A-Za-z0-9+\\-*_]*" # copied from .g4 file
STR_SIMPLE_3 = "[ABCEFGHIJKLMNOPQRSTUVWXYZaceghjkmopqrstvwxz+\\-*_]+[A-Za-z0-9+\\-*._]*" # copied from .g4 file
STR_SIMPLE = "(%s)|(%s)|(%s)"%(STR_SIMPLE_1,STR_SIMPLE_2,STR_SIMPLE_3)

STR_SIMPLE_RGX = re.compile(STR_SIMPLE)

CMD_INDENT = '    ' #one level of indent are 4 spaces


def CharAllowed(c,whitelistdict):
    try:
        return whitelistdict[c]
    except KeyError:
        return False

class Eoq3TextAntlrErrorListener(ErrorListener):
    #@override
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise EOQ_ERROR_INVALID_VALUE("line %d:%d %s"%(line,column,msg))

class Eoq3TextAntlrListener(eoq3Listener):
    def __init__(self):
        super().__init__()
        self.stack:List[Any] = []  #initialize the stack
        self.indent:List[int] = [] #initialize the indent counter
        self.stackTop = 0
        self.indentLevel = -1  # initialize to -1 to make sure level 0 is initialized when entered

    def __HandleIndent(self,currentIndent:int,ctx):
        ''' handle indent for forming compound commands
        '''
        if(self.indentLevel == currentIndent): #no change in indent
            self.indent[currentIndent] += 1
        elif(self.indentLevel+1 == currentIndent):# indent
            self.indentLevel = currentIndent
            self.indent.append(1)
        elif(self.indentLevel > currentIndent):# dedent
            self.__Dedent(currentIndent)
            self.indent[currentIndent] += 1
        else: 
            raise EOQ_ERROR_INVALID_VALUE('Incorrect indent at %s'%(ctx.getText()))
        
    def __Dedent(self,currentIndent:int):
        while(self.indentLevel > currentIndent):
            #get all indented cmds
            cmds = self.__RemovePddArgs(self.__PopN(self.indent[self.indentLevel]))
            father = self.__Pop()
            if(isinstance(father,Cmp)): #explicit cmp command
                for c in cmds:
                    father.Append(c)
                self.__Push(father)
            else: #implicit cmp command
                self.__Push(father) #this was not a cmp, put it pack
                newFather = Cmp(cmds)
                self.__Push(newFather)
                self.indent[self.indentLevel-1] += 1
            self.indentLevel -= 1
            self.indent.pop()
         
    def GetResult(self):
        return self.__Pop()
        
    def exitCmds(self, ctx):
        #make sure commands are dedented to zero again
        self.__Dedent(0)
        #prepare return value, which is either a single command or a compound
        nCmds = self.indent[0]
        if(1==nCmds):
            pass #do nothing since the cmd is already on the stack
        else:
            #create a compound command
            cmds = self.__PopN(nCmds)
            cmd = Cmp(self.__RemovePddArgs(cmds)) #remove padding commands
            self.__Push(cmd)
         
    def exitCmd(self, ctx):
        cmdIdStr = ctx.CMD_ID().getText()
        #mute
        mute = False
        cmdId = cmdIdStr[0:3]
        if('-' == cmdIdStr[0]):
            mute = True
            cmdId = cmdIdStr[1:4] 
        #res name: handle first, because res name is last on stack
        resName = None
        if ctx.cmd_res_name():
            resName = self.__Pop().GetVal()
        #args
        nArgs = len(ctx.cmd_arg())
        args = self.__PopN(nArgs)
        # indent handling
        currentIndent = len(ctx.CMD_INDENT())
        self.__HandleIndent(currentIndent, ctx)
        #create command
        cmd = None
        if(CMD_TYPE_PDD == cmdId):
            cmd = Pdd()
        else:
            cmd = CmdFactory(cmdId,args,mute,resName)
        #push parsed cmd
        self.__Push(cmd)
             
    # handle primitives  
    def exitVal_bol(self,ctx):
        strVal = ctx.getText()
        val = BOL(1 == int(strVal[1])) #second char can be '0' or '1'
        self.__Push(val)
         
    def exitVal_u32(self,ctx):
        strVal = ctx.getText()
        val = U32(int(strVal[1:])) #remove the first char
        self.__Push(val)
         
    def exitVal_u64(self,ctx):
        strVal = ctx.getText()
        val = U64(int(strVal[1:])) #remove the first char
        self.__Push(val)
         
    def exitVal_i32(self,ctx):
        strVal = ctx.getText()
        val = I32(int(strVal[1:])) #remove the first char
        self.__Push(val)
         
    def exitVal_i64(self,ctx):
        strVal = ctx.getText()
        val = I64(int(strVal[1:])) #remove the first char
        self.__Push(val)
         
    def exitVal_f32(self,ctx):
        strVal = ctx.getText()
        val = F32(float(strVal[1:])) #remove the first char
        self.__Push(val)
     
    def exitVal_f64(self,ctx):
        strVal = ctx.getText()
        val = F64(float(strVal[1:])) #remove the first char
        self.__Push(val)
     
    def exitVal_str_simple(self, ctx):
        val = STR(ctx.getText())
        self.__Push(val)
         
    def exitVal_str_quote(self, ctx):
        quotedStr = ctx.getText()
        val = STR(quotedStr[1:-1].replace("\\\'","'").replace("\\\\","\\")) #the surrounding quotes and replace escape characters
        self.__Push(val)
         
    def exitVal_dat(self,ctx):
        #initialize 0 date
        Y = 0; M = 0; D=0 #year, month, day
        h = 0; m = 0; s= 0 #hour, minute, second
        u = 0.0 #microseconds
        z = 0 #timezone
        #time is mandatory
        datetimeStr = ctx.getText()
        dStart = datetimeStr.find('D')
        tStart = datetimeStr.find('T')
        uStart = datetimeStr.find('U')
        zStart = datetimeStr.find('Z')
        if(0<=dStart): #optional
            dateSegs = datetimeStr[dStart+1:dStart+11].split('-') #expecting 0000-00-00
            Y = int(dateSegs[0]); M = int(dateSegs[1]); D = int(dateSegs[2])
        if(0<=tStart): #mandatory
            timeSegs = datetimeStr[tStart+1:tStart+9].split('.') #expecting 00.00.00
            h = int(timeSegs[0]); m = int(timeSegs[1]); s = int(timeSegs[2])
        if(0<=uStart):
            if(0<=zStart):
                u = float(datetimeStr[uStart+1:zStart])
            else:
                u = float(datetimeStr[uStart+1:])
        if(0<=zStart):
            z = float(datetimeStr[zStart+1:])
        val = DAT(Y,M,D,h,m,s,u,z) 
        self.__Push(val)
         
    def exitVal_non(self,ctx):
        val = NON()
        self.__Push(val)
         
    def exitVal_lst(self,ctx):
        nElems = len(ctx.val()) #determine the length of the list
        val = self.__PopN(nElems) #remove those elements from the list ...
        self.__Push(LST(val))   #... and push it back as a nested list.
         
    def exitVal_qry(self,ctx):
        nSegs = len(ctx.qry_seg()) #determine the length of the list
        try:
            segs = self.__PopN(nSegs) #remove those elements from the list ...
        except Exception as e: #TODO: remove this if problems with special constraint 
            print("TXTSER FAILED: %s"%(str(ctx.getText())))
            raise e
        qry = Qry(segs)
        self.__Push(qry)   #... and push it back as a nested list.
         
    def exitQry_seg(self,ctx):
        nArgs = len(ctx.qry_arg()) #determine the length of the list
        try:
            args = self.__PopN(nArgs) #remove those elements from the list ...
        except Exception as e: #TODO: remove this if problems with special constraint 
            print("TXTSER FAILED: %s"%(str(ctx.getText())))
            print("TXTSER STACK: %s"%(str(self.stack)))
            raise e
        segType = self.__Pop() #the segment type was stored before the arguments
        seg = Seg(segType,args)
        self.__Push(seg)   #... and push it back as a nested list.
         
    def exitQry_sym_short(self,ctx):
        shortSym = ctx.getText() #a single char
        try:
            segType = QRY_SYMBOLS_LOT[shortSym]
            self.__Push(segType)
        except KeyError:
            raise EOQ_ERROR_INVALID_VALUE('Unknown query segment: %s'%(shortSym))
         
    def exitQry_sym_full(self,ctx):
        full = ctx.getText() # a three letter char starting with &
        segType = full[1:]
        if(segType in QRY_SYMBOLS): #this just tests if the symbol is known
            self.__Push(segType)
        else:
            raise EOQ_ERROR_INVALID_VALUE('Unknown query segment: %s'%(full))
     
    def __Pop(self):
        if(self.stackTop-1 >= 0):
            self.stackTop -= 1
            return self.stack.pop()
        else:
            raise EOQ_ERROR_RUNTIME('Can not pop element from stack. Stack is empty')
         
    def __PopN(self,n=1)->List[Any]:
        if(self.stackTop-n >= 0):
            self.stackTop -= n
            return [self.stack.pop(i) for i in range(-n,0)]
        else:
            raise EOQ_ERROR_RUNTIME('Can not pop %d elements from stack. Stack has only %d elements.'%(n,self.stackTop))
         
    def __Push(self,v):
        self.stack.append(v)
        self.stackTop += 1

    def __RemovePddArgs(self, args:List[Any])->List[Any]:
        '''Remove padding commands from the list of arguments
        Returns the list of arguments without padding commands
        '''
        return [a for a in args if not isinstance(a,Pdd)]


class TextSerializer(Serializer):
    ''' A text serializer based on Antlr 4
    Args:
        skipDefaultValues:bool (default=True): if true the command
            serializer will leave out arguments that have default values if
            at the end of the command
    
    '''
    def __init__(self,skipDefaultValues:bool=True):
        #settings
        self.skipDefaultValues = skipDefaultValues
        #initialization
        self.errorListener = Eoq3TextAntlrErrorListener()

    def Name(self):
        '''Returns a three letter identifier for this kind of serialization 
        '''
        return 'TXT'
    
    ### SERIALIZATION

    # @Overrides
    def SerFrm(self, frm:Frm)->str:
        '''Textual frames have a fixed length, which simplifies deserialization'''
        sid = '' if None==frm.sid else frm.sid
        return "AMI|%8s|%3s|%0.8x|%36s|%3s|%1d\n%s"%(frm.ver.ljust(8, ' '),frm.typ,frm.uid,sid,frm.ser,frm.roc,frm.dat)
    
    # @Override
    def SerCmd(self, cmd:Cmd)->str:
        return self.__SerCmdRaw(cmd,0,False)
    
    def __SerCmdRaw(self, cmd:Cmd, level:int, forceCmp:bool)->str:
        indentStr = ''.join([CMD_INDENT for i in range(level-1)]) #-1 = no indent for first level
        if(isinstance(cmd,Cmp)):
            nCmd = len(cmd.a) #number of subcommands
            prefix = ''
            cmdStrs = []
            isAfterCmp = True #the first command is always after a cmp
            # serialize all subcommands
            for c in cmd.a: 
                cmdStrs.append(self.__SerCmdRaw(c,level+1,isAfterCmp))
                isAfterCmp = isinstance(c,Cmp)
            # padding for 0 and 1 command cmps
            if(1 == nCmd):  # special case, because a cmp with only one subcommand cannot be distinguished from a single command
                # pad by one PDD command
                cmdStrs.append(self.__SerCmdRaw(Pdd(),level+1,False))
            elif(0 == nCmd): #special case, because an empty cmp results in no serialization
                # pad by two PDD command
                cmdStrs.append(self.__SerCmdRaw(Pdd(), level + 1, False))
                cmdStrs.append(self.__SerCmdRaw(Pdd(), level + 1, False))
            # serialize the cmp itself if necessary, i.e. mute or result name is set, but not on the first level
            if(level>0 and (forceCmp or cmd.m or None != cmd.r)):# the first cmp is implicit if no mute or result name is specified
                prefix = indentStr+self.__SerCmdMute(cmd)+cmd.cmd+self.__SerCmdResName(cmd)+'\n'
            return prefix + ('\n'.join(cmdStrs))
        else:
            mandArgs = []
            cmdInfo = GetCmdInfo(cmd.cmd)
            if(None != cmdInfo and self.skipDefaultValues):
                #if command is known, show only optional arguments with a value different from the default.
                #find out how many optional args have values identical to the default value, i.e find the first optional argument with an non-default value
                lastNonDefaultOptArg = 0
                for i in range(cmdInfo.optArgs):
                    if(not ValCompare(cmd.a[cmdInfo.minArgs+i],cmdInfo.optDefVals[i])):
                        lastNonDefaultOptArg = i+1
                #strip the optional arguments as long as they match their default value
                mandArgs = cmd.a[0:cmdInfo.minArgs+lastNonDefaultOptArg]
            else:
                mandArgs = cmd.a
            argStrs = [' '+self.SerVal(a) for a in mandArgs]
            return indentStr+self.__SerCmdMute(cmd)+cmd.cmd+(''.join(argStrs))+self.__SerCmdResName(cmd)
        
    def __SerCmdMute(self, cmd:Cmd):
        return ('-' if cmd.m else '')
    
    def __SerCmdResName(self, cmd:Cmd):
        return ((' -> $'+self._SerStr(cmd.r)) if cmd.r else '')
        
    # @Override    
    def SerQry(self, qry:QRY)->str:
        segStrs = [self.SerSeg(s) for s in qry.v]
        return '('+''.join(segStrs)+')'
    
    # @Override
    def SerSeg(self, seg:Seg)->str:
        argStrs = [self.SerVal(a) for a in seg.v]
        return QRY_SYMBOLS[seg.seg]+';'.join(argStrs)
    
    # @Override    
    def SerVal(self, val:VAL)->str:
        if(isinstance(val,NON)): 
            return 'n0'
        elif(isinstance(val,BOL)): 
            return 'b1' if val.v else 'b0'
        elif(isinstance(val,U32)): 
            return 'u%d'%(val.v)
        elif(isinstance(val,U64)): 
            return 'y%d'%(val.v)
        elif(isinstance(val,I32)): 
            return 'i%d'%(val.v)
        elif(isinstance(val,I64)): 
            return 'l%d'%(val.v)
        elif(isinstance(val,F32)): 
            return ('f%f'%(val.v)).rstrip('0').rstrip('.') #remove trailing 0 and .
        elif(isinstance(val,F64)): 
            return ('d%f'%(val.v)).rstrip('0').rstrip('.') #remove trailing 0 and .
        elif(isinstance(val,STR)): 
            return self._SerStr(val.v)
        elif(isinstance(val,DAT)): 
            return 'D%04d-%02d-%02dT%02d.%02d.%02dU%010.7fZ%+06.2f'%(val.year(),val.month(),val.day(),val.hour(),val.minute(),val.second(),val.microsec(),val.utcoff())
        elif(isinstance(val,QRY)):
            return self.SerQry(val)
        elif(isinstance(val,LST)): #list must be the after str, because str is also a list
            valStrs = [self.SerVal(v) for v in val.v] #cannot use Val() here, because that decomposes the full list
            return '['+','.join(valStrs)+']'
        else:
            raise EOQ_ERROR_INVALID_TYPE("Unknown value type %s."%(type(val).__name__))
    
    # @Override
    def _SerStr(self,val:str)->str:
        n = len(val)
        if(0 == n):
            return self._SerStrComplex(val)
        elif(STR_SIMPLE_RGX.fullmatch(val)):
            return val
        else:
            return self._SerStrComplex(val)
        
    def _SerStrComplex(self, val:str):
            return "'"+val.replace("\\", "\\\\").replace("'", "\\'")+"'"  
        
        
    #DESERIALIZATION   
    def __Parse(self, text):
        lexerInput = InputStream(text)
        lexer = eoq3Lexer(lexerInput) #input stream is provided later
        lexer.removeErrorListeners()
        lexer.addErrorListener(self.errorListener)
        stream = CommonTokenStream(lexer)
        parser = eoq3Parser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(self.errorListener)
        return parser

    def __Construct(self, tree):
        constructListener = Eoq3TextAntlrListener()
        walker = ParseTreeWalker()
        walker.walk(constructListener, tree)
        res = constructListener.GetResult()
        return res
    
    # @Override
    def DesFrm(self,data:str)->Frm:
        '''the frame length is not checked'''
        #"AMI|%8s|%3s|%8x|%36s|%3s\n%s"(frm.ver,frm.typ,frm.uid,frm.sid,frm.ser,frm.dat)
        #Example:
        #AMI|33.22.11|CMD|3ade68b1|95103b3e-293c-48d6-9c07-2f97e4ab3690|TXT
        #    4        13  17       26                                   63
        ver = data[4:12].split(' ')[0] #only keep the part until the first blank
        typ = data[13:16]
        uid = int(data[17:25],base=16)
        sid = data[26:62]
        #sids that do not fill the first char are assumed as none
        sid = None if sid[0] == ' ' else sid
        ser = data[63:66]
        roc = bool(int(data[67:68]))
        dat = data[69:]
        return Frm(typ, uid, ser, dat, sid, roc, ver)
    
    # @Override
    def DesCmd(self,data:str)->Cmd:
        parser = self.__Parse(data)
        tree = parser.cmds()
        cmd = self.__Construct(tree)
        return cmd
    
    # @Override
    def DesQry(self, data:str)->Qry:
        parser = self.__Parse(data)
        tree = parser.val_qry()
        qry = self.__Construct(tree)
        return qry
    
    # @Override
    def DesSeg(self, data:str)->Seg:
        parser = self.__Parse(data)
        tree = parser.qry_seg()
        seg = self.__Construct(tree)
        return seg
    
    # @Override
    def DesVal(self, data:str):
        parser = self.__Parse(data)
        tree = parser.val()
        val = self.__Construct(tree)
        return val
    
### make this serializer known globally 
RegisterSerializer(TextSerializer)