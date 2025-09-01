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



class PySerializer(Serializer):
    '''Python Serializer   
    '''
    # @Overrides 
    def Name(self)->str:           
        return "PYT"
    # @Overrides 
    def SerFrm(self, frm:Frm)->str:
        return "Frm('%s',%d,'%s','%s','%s',%s,'%s')"%(frm.typ,frm.uid,frm.ser,frm.dat.replace("\\","\\\\").replace("'","\\'"),frm.sid,"True" if frm.roc else "False",frm.ver);
    
    # @Override
    def SerCmd(self, cmd:Cmd):
        return self.__SerCmdRaw(cmd,0)
    
    def __SerCmdRaw(self, cmd:Cmd, level:int):
        if(isinstance(cmd,Cmp)):
            cmdStrs = ['.' + self.__SerCmdRaw(c,level+1) for c in cmd.a]
            if(0==level):
                return "Cmp("+self.__CmdMuteResNameStr(cmd,"")+")"+"".join(cmdStrs)
            else:
                return "Append(Cmp("+self.__CmdMuteResNameStr(cmd,"")+")"+"".join(cmdStrs)+")"
        else:
            argStrs = [self.SerVal(a) for a in cmd.a]
            cmdInfo = GetCmdInfo(cmd.cmd)
            if(None != cmdInfo):
                if(cmdInfo.unpackArgs):
                    return "%s(%s%s)"%(self.__ToPyName(cmd.cmd),",".join(argStrs),self.__CmdMuteResNameStr(cmd,("," if 0<len(argStrs) else "")))
                else:
                    return "%s([%s]%s)"%(self.__ToPyName(cmd.cmd),",".join(argStrs),self.__CmdMuteResNameStr(cmd,","))
            else: #must be a custom command 
                return "Cus('%s',[%s]%s)"%(cmd.cmd,",".join(argStrs),self.__CmdMuteResNameStr(cmd,","))
        
    def __CmdMuteResNameStr(self, cmd:Cmd, prefix:str):
        segments = []
        if(cmd.m):
            segments.append("mute=True")
        if(cmd.r):
            segments.append("resName='%s'"%(cmd.r))
        if(0 < len(segments)):
            return prefix+",".join(segments)
        else:
            return ""
        
    # @Override    
    def SerQry(self, qry:Qry):
        segStrs = [self.SerSeg(s) for s in qry.v]
        return '.'.join(segStrs)
    
    # @Override
    def SerSeg(self, seg:Seg):
        argStrs = [self.SerVal(a) for a in seg.v]
        return self.__ToPyName(seg.seg)+ '(' + ','.join(argStrs) + ')'
    
    # @Override    
    def SerVal(self,val:VAL):
        if(isinstance(val,NON)): # NON must be first, because NON is also instance of many of the others
            return 'NON()'
        elif(isinstance(val,BOL)): 
            return 'BOL(True)' if val.v else 'BOL(False)'
        elif(isinstance(val,U32)): 
            return 'U32(%d)'%(val.v)
        elif(isinstance(val,U64)): 
            return 'U64(%d)'%(val.v)
        elif(isinstance(val,I32)): 
            return 'I32(%d)'%(val.v)
        elif(isinstance(val,I64)): 
            return 'I64(%d)'%(val.v)
        elif(isinstance(val,F32)): 
            return 'F32(%f)'%(val.v)
        elif(isinstance(val,F64)): 
            return 'F64(%f)'%(val.v)
        elif(isinstance(val,STR)): 
            return "STR('" + val.v.replace("\\","\\\\").replace("'","\\'") + "')"
        elif(isinstance(val,DAT)): 
            return "DAT(%d,%d,%d,%d,%d,%d,%f,%f)"%(val.year(),val.month(),val.day(),val.hour(),val.minute(),val.second(),val.microsec(),val.utcoff())
        elif(isinstance(val,QRY)):
            return self.SerQry(val)
        elif(isinstance(val,LST)): #list must be the after str, because str is also a list
            valStrs = [self.SerVal(v) for v in val.v] #cannot use Val() here, because that decomposes the full list
            return 'LST(['+','.join(valStrs)+'])'
        else:
            raise EOQ_ERROR_INVALID_TYPE("Unknown value type %s."%(type(val).__name__))
        
    def __ToPyName(self,typeStr:str)->str:
        return typeStr[0] + typeStr[1:].lower()

    def DesFrm(self, data)->Frm:
        from ..frame import Frm
        try:
            return eval(data)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Frm: %s"%(e))
    
    def DesCmd(self, data)->Cmd:
        try:
            return eval(data)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Cmd: %s"%(e))
    
    def DesQry(self, data)->Qry:
        try:
            return eval(data)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Qry: %s"%(e))
    
    def DesSeg(self, data)->Seg:
        try:
            return eval(data)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Seg: %s"%(e))
    
    def DesVal(self, data):
        try:
            return eval(data)
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Invalid Val: %s"%(e))
        
### make this serializer known globally 
RegisterSerializer(PySerializer)