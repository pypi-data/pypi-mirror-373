'''
 Bjoern Annighoefer 2019
'''

from .serializer import Serializer, RegisterSerializer

from ..value import VAL, BOL, U32, U64, I32, I64, F32, F64, STR, DAT, NON, QRY, LST
#import all queries because the eval function needs them
from ..query import Seg, Qry, Obj, Oni, His, Pth, Cls, Ino, Try, Met, Qrf, Stf, Slf, Not, Idx, Sel, Arr, Zip, Any, All, Equ, Eqa, Neq, Les, Gre, Rgx
#import all commands because the eval function needs them
from ..command import Cmd, Red, Get, Upd, Del, Set, Add, Rem, Mov, Clo, Crt, Hel, Ses, Gby, Sts, Chg, Obs, Ubs, Msg, Ver, Gac, Res, Err, Evt, Scc, Ucc, Cus, Cmp, GetCmdInfo
from ..frame import Frm
from ..error import EOQ_ERROR_INVALID_TYPE, EOQ_ERROR_INVALID_VALUE


JS_FRM_PREFIX = "new FRM."
JS_CMD_PREFIX = "new CMD."
JS_QRY_PREFIX = "new QRY."
JS_VAL_PREFIX = "new VAL."

class JsSerializer(Serializer):
    '''Javascript Serializer   
    '''
    # @Overrides 
    def Name(self)->str:           
        return "JSC"
    # @Overrides 
    def SerFrm(self, frm:Frm)->str:
        return JS_FRM_PREFIX+"Frm('%s',%d,'%s','%s','%s',%s,'%s')"%(frm.typ,frm.uid,frm.ser,frm.dat.replace("\\","\\\\").replace("'","\\'"),frm.sid,"true" if frm.roc else "false",frm.ver)
    
    # @Override
    def SerCmd(self, cmd:Cmd)->str:
        return JS_CMD_PREFIX+self.__SerCmdRaw(cmd,0)
        
    def __SerCmdRaw(self, cmd:Cmd, level:int):
        if(isinstance(cmd,Cmp)):
            cmdStrs = ['.' + self.__SerCmdRaw(c,level+1) for c in cmd.a]
            if(0==level):
                return "Cmp("+self.__CmdMuteResNameStr(cmd,"[],")+")"+"".join(cmdStrs)
            else:
                return "Append("+JS_CMD_PREFIX+"Cmp("+self.__CmdMuteResNameStr(cmd,"[],")+")"+"".join(cmdStrs)+")"
        else:
            argStrs = [self.SerVal(a) for a in cmd.a]
            cmdInfo = GetCmdInfo(cmd.cmd)
            if(None != cmdInfo):
                if(cmdInfo.unpackArgs):
                    return "%s(%s%s)"%(self.__ToJsName(cmd.cmd),",".join(argStrs),self.__CmdMuteResNameStr(cmd,("," if 0<len(argStrs) else "")))
                else:
                    return "%s([%s]%s)"%(self.__ToJsName(cmd.cmd),",".join(argStrs),self.__CmdMuteResNameStr(cmd,","))
            else: #must be a custom command 
                return "Cus('%s',[%s]%s)"%(cmd.cmd,",".join(argStrs),self.__CmdMuteResNameStr(cmd,","))
        
    def __CmdMuteResNameStr(self, cmd:Cmd, prefix:str):
        segments = []
        if(cmd.m):
            segments.append("true")
        elif(cmd.r): #not mute but resname
            segments.append("false")
        if(cmd.r): #check a second time without the precondition that mute must be false
            segments.append("'%s'"%(cmd.r))
        if(0 < len(segments)):
            return prefix+",".join(segments)
        else:
            return ""
        
    # @Override    
    def SerQry(self,qry:Qry):
        segStrs = [self.SerSeg(s) for s in qry.v]
        return JS_QRY_PREFIX + '.'.join(segStrs)
    
    # @Override
    def SerSeg(self, seg:Seg):
        argStrs = [self.SerVal(a) for a in seg.v]
        return self.__ToJsName(seg.seg)+ '(' + ','.join(argStrs) + ')'
    
    # @Override    
    def SerVal(self, val:VAL):
        if(isinstance(val,NON)): 
            return JS_VAL_PREFIX + 'NON()'
        elif(isinstance(val,BOL)): 
            return JS_VAL_PREFIX + ('BOL(true)' if val.v else 'BOL(false)')
        elif(isinstance(val,U32)): 
            return JS_VAL_PREFIX + 'U32(%d)'%(val.v)
        elif(isinstance(val,U64)): 
            return JS_VAL_PREFIX + 'U64(%d)'%(val.v)
        elif(isinstance(val,I32)): 
            return JS_VAL_PREFIX + 'I32(%d)'%(val.v)
        elif(isinstance(val,I64)): 
            return JS_VAL_PREFIX + 'I64(%d)'%(val.v)
        elif(isinstance(val,F32)): 
            fstr = ('%f'%(val.v)).rstrip('0').rstrip('.') #remove trailing 0 and .
            return JS_VAL_PREFIX + 'F32(%s)'%(fstr) #remove trailing 0 and .
        elif(isinstance(val,F64)): 
            fstr = ('%f'%(val.v)).rstrip('0').rstrip('.') #remove trailing 0 and .
            return JS_VAL_PREFIX + 'F64(%s)'%(fstr) #remove trailing 0 and .
        elif(isinstance(val,STR)): 
            return JS_VAL_PREFIX + "STR('" + val.v.replace("\\","\\\\").replace("'","\\'") + "')"
        elif(isinstance(val,DAT)):
            us = ('%f'%(val.microsec())).rstrip('0').rstrip('.') #remove trailing 0 and .
            of = ('%f'%(val.utcoff())).rstrip('0').rstrip('.') #remove trailing 0 and .
            return JS_VAL_PREFIX + "DAT(%d,%d,%d,%d,%d,%d,%s,%s)"%(val.year(),val.month(),val.day(),val.hour(),val.minute(),val.second(),us,of)
        elif(isinstance(val,QRY)):
            return self.SerQry(val)
        elif(isinstance(val,LST)): #list must be the after str, because str is also a list
            valStrs = [self.SerVal(v) for v in val.v] #cannot use Val() here, because that decomposes the full list
            return JS_VAL_PREFIX + 'LST(['+','.join(valStrs)+'])'
        else:
            raise EOQ_ERROR_INVALID_TYPE("Unknown value type %s."%(type(val).__name__))
        
    def __ToJsName(self,typeStr:str)->str:
        return typeStr[0] + typeStr[1:].lower()

    def DesFrm(self, data)->Frm:
        try:
            pyexpr = self.__JsToPyConverter(data) #transform js to python
            return eval(pyexpr)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Frm: %s"%(e))
    
    def DesCmd(self, data)->Cmd:
        try:
            pyexpr = self.__JsToPyConverter(data) #transform js to python
            return eval(pyexpr)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Cmd: %s"%(e))
    
    def DesQry(self, data)->Qry:
        try:
            pyexpr = self.__JsToPyConverter(data) #transform js to python
            return eval(pyexpr)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Qry: %s"%(e))
    
    def DesSeg(self, data)->Seg:
        try:
            pyexpr = self.__JsToPyConverter(data) #transform js to python
            return eval(pyexpr)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Seg: %s"%(e))
    
    def DesVal(self, data):
        try:
            pyexpr = self.__JsToPyConverter(data) #transform js to python
            return eval(pyexpr)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Val: %s"%(e))
        
    def __JsToPyConverter(self, jsexpr:str)->str:
        ''' A very simple and non-safe converter of EOQ Javascript expressions to Python expressions
        '''
        jssegs = jsexpr.split("'")
        pysegs = []
        
        isQuotedStr = False
        for i in range(len(jssegs)):
            jsseg = jssegs[i]
            #find out if this is a quoted segment
            if(0==i):
                pass #the first segment is never quoted
            else:
                #count the number of \ prior to the '
                nBackslash = 0
                for j in range(len(pysegs[i-1])-1,-1,-1):
                    if(pysegs[i-1][j] == "\\"):
                        nBackslash += 1
                    else:
                        break;
                #only even backslashes terminate the quote
                if(isQuotedStr and nBackslash%2 == 1):
                    pass #no toggle, because a quoted str was hit
                else:
                    isQuotedStr = not isQuotedStr #normally, this toggles at every segment
            
            #depending on the type of segments replace keywords or not
            if(isQuotedStr):
                pysegs.append(jsseg)
            else:
                pysegs.append(jsseg.replace("true","True").replace("false","False").replace(JS_CMD_PREFIX,"").replace(JS_QRY_PREFIX,"").replace(JS_VAL_PREFIX,"").replace(JS_FRM_PREFIX,""))
        return "'".join(pysegs)
        
### make this serializer known globally 
RegisterSerializer(JsSerializer)