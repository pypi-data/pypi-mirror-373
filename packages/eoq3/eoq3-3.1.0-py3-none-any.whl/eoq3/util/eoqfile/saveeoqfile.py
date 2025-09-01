'''
 Bjoern Annighoefer 2024
'''

from ...domain import Domain
from ...value import STR
from ...query import Obj, Qry
from ...command import Get
from ...concepts import CONCEPTS, MXELEMENT
from ...error import EOQ_ERROR_INVALID_VALUE

from .cmdstream import FromDomainCmdStream, ResNameGenStream, EoqFileOutStream, DependencyResolverStream, ObjToHisStream
from .resnamegen import FromDomainResNameGen

def SaveEoqFile(outfile:str, rootObj:Obj, domain:Domain, sessionId:str=None):
    '''Save a model to an eoqfile
    '''
    #build stream pipeline
    inStream = FromDomainCmdStream(domain,sessionId)
    sorter = DependencyResolverStream(True,False)
    renamer = ResNameGenStream(FromDomainResNameGen(domain,sessionId))
    tohist = ObjToHisStream()
    outStream = EoqFileOutStream(outfile)
    inStream.Connect(sorter)
    sorter.Connect(renamer)
    renamer.Connect(tohist)
    tohist.Connect(outStream)
    #run stream pipeline
    inStream.Begin()
    inStream.LoadElement(rootObj)
    inStream.Flush()
    