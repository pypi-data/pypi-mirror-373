'''
 CmdStream are instances that produce, transform or consume a sequence of commands

 Bjoern Annighoefer 2024
'''

from ...domain import Domain
from ...value import VAL, U32, I64, STR, LST, NON
from ...query import Qry, Obj, His, IsObj, IsHis, HisId
from ...command import CMD_TYPES, Cmd, Crt, Get, Upd
from ...concepts import *
from ...serializer import CreateSerializer
from ...error import EOQ_ERROR_INVALID_VALUE

from .eoqfileformat import CMD_SEPERATOR, LINE_COMMENT_START
from .resnamegen import ResNameGenA

from typing import Tuple, List, Dict, Set, Hashable

class CmdStreamA:
    '''Abstract base class of all command streams.
    A command stream process a series of commands.
    Each command is a tuple of command and result.
    Not all results must be real results.
    
    Different streams specializations can have 
    different pre and postconditions on streams.
    The precondition is what properties a stream must
    exhibit to be processible by the stream instance.
    Postconditions describe the stream after the 
    stream instance.
    Stream properties are described by
    - ordered: is the sequence of commands ordered such 
    that all dependencies are resolved, i.e. are 
    all elements created before used. 
    - resName: are res names assigned to cmds 
    - res: are results assigned to cmds
    - refByHis: His is used in cmds
    - refByObj: Obj is used in cmds

    stream pre and postconditions must
    match when connecting streams.

    The typical usage of a stream is 
    Begin()
    ... do something with the stream ...
    Flush()
    
    Multiple streams can be connected by calling
    Connect(next stream instance).
    Connected stream instance invove each other 
    in the connect order with the commands passing 
    by. The order of commands and calling time 
    can however be varied by some streams, like 
    dependency sorting streams.
    
    '''
    def __init__(self):
        raise NotImplementedError()
    
    def Begin(self)->None:
        '''Used to init or re-init a cmd stream. 
        Should be called before using it.
        '''
        raise NotImplementedError()
    
    def Flush(self):
        '''Force the stream to release all pending commands
        '''
        raise NotImplementedError()
    
    def PushCmd(self, cmd:Cmd, res:VAL=NON())->None:
        '''Called by the user of the writer to add a new command to the stream
        '''
        raise NotImplementedError()
        
    def WriteComment(self, comment:str):
        '''Called by the user of the writer to insert a new comment
        '''
        raise NotImplementedError()
    
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        '''Is called for every resolved command.
        Should return the a the (modified) command and result if applicable otherwise the input elements.
        Override!
        '''
        raise NotImplementedError()
    
    def OnComment(self, comment:str)->str:
        '''Is called for every released comment.
        This shall return the the (modified) comment.
        Override!
        '''
        raise NotImplementedError()
    
    def Connect(self, streamToConnect)->None:
        '''Add a stream to be called with the commands from this stream
        '''
        raise NotImplementedError()
        
    #@Override
    def Disconnect(self, streamToDisconnect)->None:
        '''Remove a command stream from the stream chain
        '''
        raise NotImplementedError()

class CmdStream(CmdStreamA):
    ''' Basic command stream. 
    Implements the basic function of a command stream:
    forwards all given commands and comments to connected streams.
    Does not modify stream properties.
    Can be extended to create more sophisticated command streams.
    
    Stream preconditions:
    - ordered: any
    - resName: any
    - res: any
    - refByHis: any
    - refByObj: any
    
    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: unchanged
    - refByHis: unchanged
    - refByObj: unchanged
    '''
    def __init__(self):
        self.nextStreams:List[CmdStreamA] = []
    
    def Begin(self):
        ''' Calls begin for all connected streams
        '''
        for s in self.nextStreams:
            s.Begin()
    
    #@Override  
    def Flush(self):
        '''Flushes all connected command streams
        '''
        for s in self.nextStreams:
            s.Flush()
    
    #@Override
    def PushCmd(self, cmd:Cmd, res:VAL=NON()):
        '''Called by the user of the writer to indicate a new command to be written
        '''
        self._ReleaseCmd(cmd, res)
    
    #@Override  
    def PushComment(self, comment:str):
        '''Called by the user of the writer to insert a new comment
        '''
        self._ReleaseComment(comment)
    
    #@Override  
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        '''Just forwards command and result unmodified.
        Override to change behavior.
        '''
        return (cmd,res)
    
    #@Override  
    def OnComment(self, comment:str)->str:
        ''' Just returns the comment.
        Override to change behavior.
        '''
        return comment
    
    #@Override
    def Connect(self, streamToConnect:CmdStreamA)->None:
        '''Add a stream to be called with the commands from this stream
        '''
        if(streamToConnect not in self.nextStreams):
            self.nextStreams.append(streamToConnect)
        
    #@Override
    def Disconnect(self, streamToDisconnect:CmdStreamA)->None:
        '''Remove a command stream from the stream chain
        '''
        if(streamToDisconnect in self.nextStreams):
            self.nextStreams.remove(streamToDisconnect)
            
    ### INTERNALS ####
            
    def _ReleaseCmd(self, cmd:Cmd, res:VAL)->VAL:
        '''Forwards a cmd to OnCmd and all connected streams.
        Connected streams are called in the order they where connected.
        Should be called within the cmd stream to indicate a cmd 
        is ready for further processing.
        '''
        (cmd,res) = self.OnCmd(cmd, res)
        for s in self.nextStreams:
            s.PushCmd(cmd,res)
        return res
            
    def _ReleaseComment(self, comment:str)->None:
        '''Forwards a cmd to OnCmd and all connected streams.
        Connected streams are called in the order they where connected.
        Should be called within the cmd stream to indicate a cmd 
        is ready for further processing.
        '''
        comment = self.OnComment(comment)
        for s in self.nextStreams:
            s.PushComment(comment)
            
class RecorderCmdStream(CmdStream):
    '''Stores all pushed cmds into an internal list.
    The list can be retrieved by GetCmds().
    
    Stream preconditions:
    - ordered: any
    - resName: any
    - res: any
    - refByHis: any
    - refByObj: any
    
    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: unchanged
    - refByHis: unchanged
    - refByObj: unchanged
    '''
    def __init__(self):
        super().__init__()
        self.cmds:List[Cmd] = None
    
    #@Override    
    def Begin(self):
        '''Restarts recording
        '''
        self.cmds = []
        CmdStream.Begin(self)
    
    #@Override
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        ''' just stores commands in an internal list'''
        self.cmds.append(cmd)
        return (cmd,res)
    
    def GetCmds(self)->List[Cmd]:
        '''Returns a non writable copy of all commands
        streamed since last Begin() call.
        '''
        return list(self.cmds)
        
class DomainWrapperStream(CmdStream,Domain):
    '''Wraps a domain and forwards all commands to it, while also forwarding commands to connected streams.
    This stream is useful, for instance, to record all commands while also executing them on a domain.
    Event forwarding is not supported.

    Stream preconditions:
    - ordered: no
    - resName: no
    - res: no
    - refByHis: yes
    - refByObj: yes

    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: yes if execution successful
    - refByHis: unchanged
    - refByObj: unchanged

    '''
    def __init__(self, domain:Domain):
        CmdStream.__init__(self)
        Domain.__init__(self)
        self.domain = domain

    #@Override
    def Do(self, cmd:Cmd, sessionId:str=None, asDict:bool=False, readOnly=False)->VAL:
        '''Executes a command on the domain
        '''
        #first execute the command
        res = self.domain.Do(cmd,sessionId,asDict,readOnly)
        #second forward the command to connected streams
        self._ReleaseCmd(cmd,res)
        return res

    #@Override
    def PushCmd(self, cmd:Cmd, res:VAL=NON()):
        ''' Not supported
        '''
        raise NotImplementedError()
            
class DependencyResolverStream(CmdStream):
    '''A command stream implementation, sorting comments according to their dependencies and issue
    commands only for writing, if dependencies have been resolved.
    
    Stream preconditions:
    - ordered: no
    - resName: yes if resolveHis
    - res: yes if resolveObj
    - refByHis: yes if resolveHis
    - refByObj: yes if resolveObj
    
    Stream postconditions:
    - ordered: yes
    - resName: unchanged
    - res: unchanged
    - refByHis: unchanged
    - refByObj: unchanged
    
    '''
    def __init__(self, resolveObj:bool=True, resolveHis:bool=True):
        super().__init__()
        self.resolveObj = resolveObj
        self.resolveHis = resolveHis
        #internals
        self.cmdQueue:List[Tuple[Cmd,VAL,Set[Hashable]]] = None
        self.resolvedDependencies:Set[Hashable]= None #stores references already seen
        
    #@Override
    def Begin(self)->None:
        self.cmdQueue = []
        self.resolvedDependencies = set()
        super().Begin()
        
    #@Override
    def Flush(self)->None:
        nUnresolvedCmds = len(self.cmdQueue)
        if(0<nUnresolvedCmds):
            print("Warning: %d commands have unresolved dependencies."%(nUnresolvedCmds))
            self._ReleaseComment("Warning: %d commands have unresolved dependencies:"%(nUnresolvedCmds))
            for c in self.cmdQueue:
                self._ReleaseComment(str(c))
        super().Flush()
    
    #@Override
    def PushCmd(self, cmd:Cmd, res:VAL=NON())->None:
        '''target is the element this command creates
        '''
        unresolved = self.__CollectUnresolvedCmdDepencies(cmd)
        if(0<len(unresolved)):
            #cmd cannot be processed now. command contains unknown elements. Que it to resolve later
            self.cmdQueue.append((cmd,res,unresolved))
        else:
            rewRes = self.__WriteCmdAndUpdateLut(cmd, res)
            while(None != rewRes):
                rewRes = self.__ResolveAndWriteQueuedCmds(rewRes,cmd.r)
    
    ### INTERNALS ###
     
    def __WriteCmdAndUpdateLut(self, cmd:Cmd, res:VAL)->Obj:
        '''Returns if new a new element was added to the LUT
        '''
        if(CMD_TYPES.CRT == cmd.cmd):
            #in case this is an CRT, a new entry could be created in the LUT
            res = self._ReleaseCmd(cmd, res)
            self.__ResToLut(res, cmd.r)
            return res
        else:
            self._ReleaseCmd(cmd, res) 
            return None
        
    def __ResToLut(self, res:Obj, resName:str)->None:
        if(self.resolveObj):
            self.resolvedDependencies.add(res)
        if(self.resolveHis and None != resName):
            self.resolvedDependencies.add(His(resName))
    
    def __ResolveAndWriteQueuedCmds(self, newRes:Obj, newResName:str)->Obj:
        '''Returns true if another cmd causing a LUT was removed
        '''
        rewRes = None
        writtenCmds = []
        #process list until LUT needs to be updated
        for i in range(len(self.cmdQueue)):
            cmd, res, unresolved = self.cmdQueue[i]
            if(newRes in unresolved):
                unresolved.remove(newRes)
            if(None != newResName):
                if(His(newResName) in unresolved):
                    unresolved.remove(His(newResName))
        #after full loop is completed we can look for releasable cmds
        for i in range(len(self.cmdQueue)):
            cmd, res, unresolved = self.cmdQueue[i]
            if(0==len(unresolved)):
                rewRes = self.__WriteCmdAndUpdateLut(cmd,res)
                writtenCmds.append(i)
                if(None != rewRes):
                    break #if the LUT was updated we need to break and restart
        #remove all cmds from list that have been written
        for i in range(len(writtenCmds)):
            self.cmdQueue.pop(writtenCmds[i]-i) #-i corrects the index for already popped commands
        return rewRes
    
    def __CollectUnresolvedCmdDepencies(self, cmd:Cmd)->Set[Hashable]:
        '''See if all Obj in a command are known and replace them.
        Returns if all elements are replaced
        '''
        unresolved = self.__CollectUnresolvedListDepenciencies(cmd.a)
        return unresolved
    
    def __CollectUnresolvedListDepenciencies(self, l:Tuple[list,LST])->Set[Hashable]:
        unresolved = set()
        for i in range(len(l)):
            a = l[i]
            if(self.resolveObj and IsObj(a)):
                if(a not in self.resolvedDependencies):
                    unresolved.add(a)
            if(self.resolveHis and IsHis(a)):
                if(a not in self.resolvedDependencies):
                    unresolved.add(a)
            if(LST == type(a)):
                unresolved = unresolved.union(self.__CollectUnresolvedListDepenciencies(a))
            else:
                pass #all other values remain unconsidered
        return unresolved
    
    
class RefTypeToggleStream(CmdStream):
    ''' Utility class to change the reference type of an ordered 
    cmd stream from Obj to His or vise versa
    
    Stream preconditions:
    - ordered: yes
    - resName: yes if refByHis
    - res: yes if refByObj
    - refByHis: no if refByObj=yes
    - refByObj: no if refByHis=yes
    
    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: replaced by domain Obj
    - refByHis: replaced by domain Obj
    - refByObj: replaced by domain Obj
    
    '''
    def __init__(self, resolveObj:bool=False, resolveHis:bool=True):
        super().__init__()
        if(resolveObj and resolveHis):
            raise EOQ_ERROR_INVALID_VALUE("resolveObj and resolveHis cannot both be true.")
        self.resolveObj = resolveObj
        self.resolveHis = resolveHis
        #internals
        self.hisLut:Dict[str,Obj] = None
        self.resLut:Dict[Obj,Hashable] = None
        
    #Override
    def Begin(self):
        self.hisLut = {}
        self.resLut = {}
        super().Begin()
        
    #@Override   
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        ''' executes a given command on a domain.
        res is overwritten with the result from the domain.
        '''
        self._ResolveCmd(cmd)
        if(CMD_TYPES.CRT == cmd.cmd and None != cmd.r): #for CRT store the new results
            if(self.resolveObj):
                self.resLut[res] = His(cmd.r)
            elif(None != cmd.r):
                self.hisLut[cmd.r] = res
        return (cmd,res)
    
    ### INTERNALS ###
    
    def _ResolveCmd(self, cmd:Cmd)->None:
        '''See if all Obj in a command are known and replace them.
        Returns if all elements are replaced
        '''
        self.__ResolveList(cmd.a)
    
    def __ResolveList(self, l:Tuple[list,LST])->None:
        for i in range(len(l)):
            a = l[i]
            if(self.resolveObj and IsObj(a)):
                if(a in self.resLut):
                    l[i] = self.resLut[a]
                else:
                    raise EOQ_ERROR_INVALID_VALUE("Cannot resolve %s."%(a))
            elif(self.resolveHis and IsHis(a)):
                resName = HisId(a)
                if(resName in self.hisLut):
                    l[i] = self.hisLut[resName]
                else:
                    raise EOQ_ERROR_INVALID_VALUE("Cannot resolve %s."%(a))
            if(LST == type(a)):
                self.__ResolveList(a)
            else:
                pass #all other values remain unchanged
    
    
class ObjToHisStream(RefTypeToggleStream):
    '''Translates all Obj to His elements if res and resnames are given.
    Stream preconditions:
    - ordered: yes
    - resName: yes
    - res: yes
    - refByHis: no
    - refByObj: yes
    
    Stream postconditions:
    - ordered: yes
    - resName: yes
    - res: yes
    - refByHis: yes
    - refByObj: no
        
    '''
    def __init__(self):
        super().__init__(True,False)
        
class HisToObjStream(RefTypeToggleStream):
    '''Translates all Obj to His elements if res and resnames are given.
    Stream preconditions:
    - ordered: yes
    - resName: yes
    - res: yes
    - refByHis: yes
    - refByObj: no
    
    Stream postconditions:
    - ordered: yes
    - resName: yes
    - res: yes
    - refByHis: no
    - refByObj: yes
        
    '''
    def __init__(self):
        super().__init__(False,True)
        

class ResNameGenStream(CmdStream):
    '''Changes the res names in a cmd stream by applying a ResNameGen to all elements.
    
    Stream preconditions:
    - ordered: no
    - resName: no
    - res: partially as required by generator 
    - refByHis: any
    - refByObj: any
    
    Stream postconditions:
    - ordered: unchanged
    - resName: partially, depending on used generator 
    - res: unchanged
    - refByHis: unchanged
    - refByObj: unchanged
    
    '''
    def __init__(self, generator:ResNameGenA, inventForEmptyRes:bool = False):
        '''
        Empty res are skipped. 
        If inventForEmptyRes is true, than invent names for those as well.
        '''
        super().__init__()
        self.generator = generator
        self.inventForEmptyRes = inventForEmptyRes
        
    #@Override   
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        resName = cmd.r
        if(res.IsNone()):
            if(self.inventForEmptyRes):
                resName = self.generator.InventResName()
            else: 
                pass #do not generate a name, but keep the old value
        else:
            resName = self.generator.GenResName(res)
        cmd.r = resName
        return (cmd, res)

### DOMAIN STREAMS

class ToDomainCmdStream(RefTypeToggleStream):
    ''' Utility class to write a sequence of commands sequentially directly to a domain
    
    Stream preconditions:
    - ordered: yes
    - resName: yes if refByHis
    - res: yes if refByObj
    - refByHis: no if refByObj=yes
    - refByObj: no if refByHis=yes
    
    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: replaced by domain Obj
    - refByHis: replaced by domain Obj
    - refByObj: replaced by domain Obj
    
    '''
    def __init__(self, domain:Domain, sessionId:str, resolveObj:bool=False, resolveHis:bool=True):
        super().__init__(resolveObj,resolveHis)
        self.domain = domain
        self.sessionId = sessionId
        
    #@Override   
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        ''' executes a given command on a domain.
        res is overwritten with the result from the domain.
        '''
        if(self.resolveHis or self.resolveObj):
            self._ResolveCmd(cmd)
            newRes = self.domain.Do(cmd,self.sessionId)
            if(CMD_TYPES.CRT == cmd.cmd): #for CRT store the new results
                if(IsObj(res)):
                    self.resLut[res] = newRes
                if(None != cmd.r):
                    self.hisLut[cmd.r] = newRes
        else:
            newRes = self.domain.Do(cmd,self.sessionId)
        return (cmd,newRes)
    
    
class FromDomainCmdStream(CmdStream):
    '''Converts a model into commands
    '''
    def __init__(self, domain:Domain, sessionId:str):
        super().__init__()
        self.domain = domain
        self.sessionId = sessionId
            
    def LoadElement(self, root:Obj):
        concept = self.domain.Do( Get(Qry(root).Pth(STR(MXELEMENT.CONCEPT))) )
        if(CONCEPTS.M2MODEL==concept):
            self.LoadM2Model(root)
        elif(CONCEPTS.M1MODEL==concept):
            self.LoadM1Model(root)
        elif(CONCEPTS.MXMDB==concept):
            self.LoadMxMdb(root)
        else:
            raise EOQ_ERROR_INVALID_VALUE("root must be *M1MODEL, *M2MODEL or *MDB")
        
    def LoadMxMdb(self,  target:Obj)->None:
        m2models = self.domain.Do( Get( Qry(target).Pth(STR(MXMDB.M2MODELS))),self.sessionId)
        for m in m2models:
            self.LoadM2Model(m)
        m1models = self.domain.Do( Get( Qry(target).Pth(STR(MXMDB.M1MODELS))),self.sessionId)
        for m in m1models:
            self.LoadM1Model(m)
        
    def LoadM1Model(self, target:Obj)->None:
        name = self.domain.Do( Get( Qry(target).Pth(STR(M1MODEL.M2MODEL)).Pth(STR(MXELEMENT.STRID))),self.sessionId)
        self.__ConceptToFileCmdStream(target,CONCEPTS.M1MODEL,[M1MODEL.M2MODEL,M1MODEL.NAME],self.__MxElementToCmdStream, {M1MODEL.M2MODEL:name})
        objects = self.domain.Do( Get( Qry(target).Pth(STR(M1MODEL.OBJECTS))),self.sessionId)
        for o in objects:
            name = self.domain.Do( Get( Qry(o).Pth(STR(M1OBJECT.M2CLASS)).Pth(STR(MXELEMENT.STRID))),self.sessionId)
            self.__ConceptToFileCmdStream(o,CONCEPTS.M1OBJECT,[M1OBJECT.M2CLASS, M1OBJECT.MODEL, M1OBJECT.NAME],self.__MxElementToCmdStream, {M1OBJECT.M2CLASS:name})
            attributes = self.domain.Do( Get( Qry(o).Pth(STR(M1OBJECT.ATTRIBUTES))),self.sessionId)
            for f in attributes:
                name = self.domain.Do( Get( Qry(f).Pth(STR(M1ATTRIBUTE.M2ATTRIBUTE)).Pth(STR(M2ATTRIBUTE.NAME))),self.sessionId)
                self.__ConceptToFileCmdStream(f,CONCEPTS.M1ATTRIBUTE,[M1ATTRIBUTE.M2ATTRIBUTE,M1ATTRIBUTE.OBJECT,M1ATTRIBUTE.VALUE],self.__MxElementToCmdStream, {M1ATTRIBUTE.M2ATTRIBUTE:name})
            associations = self.domain.Do( Get( Qry(o).Pth(STR(M1OBJECT.SRCASSOCIATIONS))),self.sessionId)
            for f in associations:
                name = self.domain.Do( Get( Qry(f).Pth(STR(M1ASSOCIATION.M2ASSOCIATION)).Pth(STR(M2ASSOCIATION.DSTNAME))),self.sessionId)
                self.__ConceptToFileCmdStream(f,CONCEPTS.M1ASSOCIATION,[M1ASSOCIATION.M2ASSOCIATION,M1ASSOCIATION.SRC,M1ASSOCIATION.DST],self.__MxElementToCmdStream, {M1ASSOCIATION.M2ASSOCIATION:name})
            compositions = self.domain.Do( Get( Qry(o).Pth(STR(M1OBJECT.PARENTCOMPOSITIONS))),self.sessionId)
            for f in compositions:
                name = self.domain.Do( Get( Qry(f).Pth(STR(M1COMPOSITION.M2COMPOSITION)).Pth(STR(M2COMPOSITION.NAME))),self.sessionId)
                self.__ConceptToFileCmdStream(f,CONCEPTS.M1COMPOSITION,[M1COMPOSITION.M2COMPOSITION,M1COMPOSITION.PARENT,M1COMPOSITION.CHILD],self.__MxElementToCmdStream, {M1COMPOSITION.M2COMPOSITION:name})
    
    def LoadM2Model(self, target:Obj)->None:
        self.__ConceptToFileCmdStream(target,CONCEPTS.M2MODEL,[M2PACKAGE.NAME],self.__M2PackageFeaturesToCmdStream)
    
    def __MxElementToCmdStream(self, target:Obj)->None:
        docu = self.domain.Do( Get( Qry(target).Pth(STR(MXELEMENT.DOCUMENTATION))),self.sessionId)
        if(not docu.IsNone()):
            self.PushCmd(Upd(target,STR(MXELEMENT.DOCUMENTATION),docu), NON())
        owner = self.domain.Do( Get( Qry(target).Pth(STR(MXELEMENT.OWNER))),self.sessionId)
        if(not owner.IsNone()):
            self.PushCmd(Upd(target,STR(MXELEMENT.OWNER),owner), NON())
        group = self.domain.Do( Get( Qry(target).Pth(STR(MXELEMENT.GROUP))),self.sessionId)
        if(not owner.IsNone()):
            self.PushCmd(Upd(target,STR(MXELEMENT.GROUP),group), NON())
        permissions = self.domain.Do( Get( Qry(target).Pth(STR(MXELEMENT.PERMISSIONS))),self.sessionId)
        for p in permissions:
            self.PushCmd(Upd(target,STR(MXELEMENT.PERMISSIONS),p,I64(-1)), NON())
        constraints = self.domain.Do( Get( Qry(target).Pth(STR(MXELEMENT.CONSTRAINTS))),self.sessionId)
        for c in constraints:
            expression = self.domain.Do(Get( Qry(c).Pth(STR(MXCONSTRAINT.EXPRESSION))),self.sessionId)
            self.PushCmd(Crt(STR(CONCEPTS.MXCONSTRAINT),U32(1),LST([target,expression])), NON())
            self.__MxElementToCmdStream(c)
        
    def _M2PackageToFile(self, target:Obj)->None:
        self.__ConceptToFileCmdStream(target,CONCEPTS.M2PACKAGE,[M2PACKAGE.NAME,M2PACKAGE.SUPERPACKAGE],self.__M2PackageFeaturesToCmdStream)
        
    def __M2PackageFeaturesToCmdStream(self, target:Obj)->None:
        self.__MxElementToCmdStream(target)
        enums = self.domain.Do( Get( Qry(target).Pth(STR(M2PACKAGE.ENUMS))),self.sessionId)
        for e in enums:
            self.__ConceptToFileCmdStream(e,CONCEPTS.M2ENUM,[M2ENUM.NAME,M2ENUM.PACKAGE],self.__MxElementToCmdStream)
            options = self.domain.Do( Get( Qry(e).Pth(STR(M2ENUM.OPTIONS))),self.sessionId)
            for o in options:
                self.__ConceptToFileCmdStream(o,CONCEPTS.M2OPTIONOFENUM,[M2OPTIONOFENUM.NAME,M2OPTIONOFENUM.VALUE,M2OPTIONOFENUM.ENUM],self.__MxElementToCmdStream)
        classes = self.domain.Do( Get( Qry(target).Pth(STR(M2PACKAGE.CLASSES))),self.sessionId)
        for c in classes:
            self.__ConceptToFileCmdStream(c,CONCEPTS.M2CLASS,[M2CLASS.NAME,M2CLASS.ISABSTRACT,M2CLASS.PACKAGE],self.__MxElementToCmdStream)
            inheritances = self.domain.Do( Get( Qry(c).Pth(STR(M2CLASS.MYGENERALIZATIONS))),self.sessionId)
            for i in inheritances:
                self.__ConceptToFileCmdStream(i,CONCEPTS.M2INHERITANCE,[M2INHERITANCE.SUBCLASS,M2INHERITANCE.SUPERCLASS],self.__MxElementToCmdStream)
            attributes = self.domain.Do( Get( Qry(c).Pth(STR(M2CLASS.MYATTRIBUTES))),self.sessionId)
            for f in attributes:
                self.__ConceptToFileCmdStream(f,CONCEPTS.M2ATTRIBUTE,[M2ATTRIBUTE.NAME,M2ATTRIBUTE.CLASS,M2ATTRIBUTE.PRIMTYPE,M2ATTRIBUTE.MUL,M2ATTRIBUTE.UNIT,M2ATTRIBUTE.ENUM],self.__MxElementToCmdStream)
            associations = self.domain.Do( Get( Qry(c).Pth(STR(M2CLASS.MYSRCASSOCIATIONS))),self.sessionId)
            for f in associations:
                self.__ConceptToFileCmdStream(f,CONCEPTS.M2ASSOCIATION,[M2ASSOCIATION.SRCNAME,M2ASSOCIATION.SRCCLASS,M2ASSOCIATION.SRCMUL,M2ASSOCIATION.DSTNAME,M2ASSOCIATION.DSTCLASS,M2ASSOCIATION.DSTMUL,M2ASSOCIATION.ANYDST],self.__MxElementToCmdStream)
            compositions = self.domain.Do( Get( Qry(c).Pth(STR(M2CLASS.MYPARENTCOMPOSITIONS))),self.sessionId)
            for f in compositions:
                self.__ConceptToFileCmdStream(f,CONCEPTS.M2COMPOSITION,[M2COMPOSITION.NAME,M2COMPOSITION.PARENTCLASS,M2COMPOSITION.CHILDCLASS,M2COMPOSITION.MULCHILD,M2COMPOSITION.ANYCHILD],self.__MxElementToCmdStream)
            packages = self.domain.Do( Get( Qry(target).Pth(STR(M2PACKAGE.SUBPACKAGES))),self.sessionId)
        for p in packages:
            self._M2PackageToFile(p)
    
    def __ConceptToFileCmdStream(self, target:Obj, conceptId:str, createArgNames:List[str], superClassCall=None, caReplacements:Dict[str,VAL]={}):
        createArgs = []
        for n in createArgNames:
            if(n in caReplacements):
                createArgs.append(caReplacements[n])
            else:
                createArgs.append(self.domain.Do( Get( Qry(target).Pth(STR(n))),self.sessionId))
        cmd = Crt(STR(conceptId),U32(1),LST(createArgs))
        self.PushCmd(cmd, target)
        if(None!=superClassCall):
            superClassCall(target)


### EOQFILE STREAMS ###
    
    
class EoqFileOutStream(CmdStream):
    ''' Utility class to write a sequence of commands sequentially to a file.
    
    Stream preconditions:
    - ordered: yes (only EOQ file shall contain ordered cmds)
    - resName: yes
    - res: any (is not used)
    - refByHis: yes (EOQ files are reference by His)
    - refByObj: no
    
    Stream postconditions:
    - ordered: unchanged
    - resName: unchanged
    - res: unchanged
    - refByHis: unchanged
    - refByObj: unchanged
    
    '''
    def __init__(self, outfile:str, serializerType:str = "TXT"):
        super().__init__()
        self.outfile = outfile
        self.serializer = CreateSerializer(serializerType)
    
    #@Override
    def Begin(self):
        self.file = open(self.outfile,"w")
        super().Begin()
        
    #@Override   
    def OnCmd(self, cmd:Cmd, res:VAL)->Tuple[Cmd,VAL]:
        strCmd = self.serializer.SerCmd(cmd)
        self.file.write(strCmd)
        self.file.write(CMD_SEPERATOR)
        return (cmd, res)
    
    #@Override 
    def OnComment(self, comment:str)->str:
        self.file.write(LINE_COMMENT_START)
        self.file.write(comment)
        self.file.write(CMD_SEPERATOR)
        return comment
    
    #@Override  
    def Flush(self)->None:
        if(self.file):
            self.file.close()
        super().Flush()
        
        
class EoqFileInStream(CmdStream):
    ''' Utility class to read a stream of commands sequentially from a file.
    
    Stream preconditions:
    - (shall not be used after other stream)
    
    Stream postconditions:
    - ordered: yes (only EOQ file shall contain ordered cmds)
    - resName: yes
    - res: any (is not used)
    - refByHis: yes (EOQ files are reference by His)
    - refByObj: no
    
    '''
    def __init__(self, serializerType:str="TXT"):
        super().__init__()
        self.serializer = CreateSerializer(serializerType)
        
    def LoadEoqFile(self, infile:str)->None:
        f = open(infile,"r")
        cmdStr = '' #stores command string until it is complete
        lineNb = 0;
        try:
            for line in f:
                lineNb += 1
                if(line.startswith(LINE_COMMENT_START)): #comment
                    self.PushComment(line[len(LINE_COMMENT_START):])
                else:
                    if(line.endswith(CMD_SEPERATOR)):
                        cmdStr += line
                        #command is complete, so execute
                        cmdStr = cmdStr[:-2]
                        cmd = self.serializer.DesCmd(cmdStr)
                        self.PushCmd(cmd)
                        #empty buffer
                        cmdStr = ''
                    else:
                        cmdStr += line
        except Exception as e:
            raise EOQ_ERROR_INVALID_VALUE("Eoq file load failed in %s line %d: %s"%(infile, lineNb, str(e)))
        finally:
            f.close()
