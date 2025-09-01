'''
Bjoern Annighoefer 2022
'''

### CONFIG CLASS ###

from typing import List, Dict, Any

class Config:
    ''' A settings struct for EOQ related classes
    '''
    def __init__(self):
        #access control
        self.superAdminName                 :str              = "superadmin" #there must always one super admin. This is how he is called
        self.defaultOwner                   :str              = "admin" # the owner of every element
        self.defaultGroup                   :str              = "users" # the default group for every unset element
        self.defaultPermission              :int              = 0xFF0 #create, delete, update and read for owner and group. None for nobody
        #remote processing
        self.remoteFrmTxSerializer          :str              = "TXT" #the default serializer used for sending remote frames
        self.remoteCmdTxSerializer          :str              = "JSO" #the default serializer used for sending remote commands
        self.remoteFrmRxSerializer          :str              = "TXT" #the serializer allowed for incoming frames. For security reasons, this should not be JSC or PYT
        self.remoteCmdRxSerializers         :List[str]        = ["TXT","JSO"] #the serializers allowed for incoming commands. All named here will be accepted. For security reasons, this should not be JSC or PYT
        self.frameVersion                   :str              = "3.0.0"
        self.threadLoopTimeout              :float            = 0.1   #[seconds] the timeout used a threaded loop waiting for events, e.g. event pull or push loops
        self.enableRawEvents                :bool             = False #do not serialize and deserialize events, which is faster, but does not allow to look inside
        self.connectTimeout                 :float            = 5.0   #[seconds] the timeout after that establishing a remote connection is assumed to be failed
        self.commandTimeout                 :float            = 10.0  #[seconds] the timeout after an established remote connection is assumed to be failed
        self.remoteRawLogging               :bool             = False # If true, remote communication is logged to files. Is only for Debug
        #eoq files
        self.fileSerializer                 :str              = "TXT" #the default serializer used for remote frames
        #command processing
        self.cmdMaxProcessingTime           :float            = None #[seconds] the maximum time a command can last before it is canceled (NOT IMPLEMENTED)
        self.cmdCmpMaxNesting               :int              = 10   #the maximum number levels of compound commands can be nested (NOT IMPLEMENTED)
        self.cmdMaxChanges                  :int              = 100  #the maximum number of changes stored in the domain
        self.cmdMaxMsgLength                :int              = 200  #the maximum number of characters in a message 
        self.cmdMaxMsgKeyLength             :int              = 15   #the maximum number of characters in a message key
        self.cmdMaxSubCommands              :int              = None #the maximum number of subcommands in a compound command (NOT IMPLEMENTED)
        self.qryMaxSegments                 :int              = None #the maximum number of segments (NOT IMPLEMENTED)
        self.resMaxElements                 :int              = None #the maximum number of elements in a result (NOT IMPLEMENTED)
        self.evtNotifyAsync                 :bool             = True #if true, event notification is handled in a thread separated from the transaction processing
        #constraitns
        self.constraintSerializer           :str              = "TXT" #the serializer for constraints
        #mdb
        self.strIdSeparator                 :str              = '__' #the separator for string IDs, e.g. package name<strIdSeparator>class name
        self.conceptsOnly                   :bool             = True #If True, mdb accepts only concept, no native elements or names
        #mpl
        self.mplMinSaveTimeout              :float            = 10.0 #[seconds] the time to wait form more changes, until the domain is persisted
        self.mplMaxSaveTimeout              :float            = 5*60.0 #[seconds] the time after a change after that persistence is enforced
        #statistics
        self.enableStatistics               :bool             = False # collect statistics/benchmark data during operation?
        #logging
        self.activeLogLevels                :int              = 0b000011 #the log levels that are active, i.e. warn and error
        self.logger                         :str              = "COL"  #the logger to use, e.g. COL = console logger, FIL = file logger, NOL = no logging, CFL = console and file logger
        self.loggerInitArgs                 :Dict[str,Any]    = {} #the arguments used to create the logger
        self.logSerializer                  :str              = "TXT" #the serializer for log entries
        #advanced debugging
        self.printExpectedExceptionTraces   :bool             = False #Shall traces of expected/caught exceptions be printed?
        self.printUnexpectedExceptionTraces :bool             = False #Shall traces of unexpected/uncaught exceptions be printed?
        self.processLessMode                :bool             = False #Threads instead of processes are used, which enables better debugging

### GLOBAL CONFIG ###
    
EOQ_DEFAULT_CONFIG = Config()
    