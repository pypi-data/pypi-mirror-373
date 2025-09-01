"""
 2025 Bjoern Annighoefer
"""

from ..domain import Domain
from ..config import Config
from ..command import Cmd
from ..error import EOQ_ERROR_ACCESS_DENIED
from ..logger import GetLoggerInstance
from ..serializer import CreateSerializer
from abc import ABC


class RemoteDomainBaseA(Domain, ABC):
    """Abstract base class for remote domains that are accessed via a network connection.
    Initialize the domain with the configuration and the logger and the serializers for incoming and outgoing data.
    """
    def __init__(self, config:Config):
        super().__init__()
        self.config = config
        self.logger = GetLoggerInstance(config)
        # create the serializers for outgoing data
        self.remoteFrmTxSerializer = CreateSerializer(config.remoteFrmTxSerializer)
        self.remoteCmdTxSerializer = CreateSerializer(config.remoteCmdTxSerializer)
        # create the serializers for incoming data
        self.remoteFrmRxSerializer = CreateSerializer(config.remoteFrmRxSerializer)
        self.remoteCmdRxSerializers = {s: CreateSerializer(s) for s in config.remoteCmdRxSerializers}

    def _DesCmd(self, serType:str, cmdStr:str) -> Cmd:
        """Deserialize a command
        Args:
        - serType: [3 letter str] the name of the serializer
        - cmdStr: The serialized command

        Returns:
        - cmd: The deserialized command
        """
        try:
            return self.remoteCmdRxSerializers[serType].DesCmd(cmdStr)
        except KeyError:
            raise EOQ_ERROR_ACCESS_DENIED("Serializer %s is not allowed for received commands" % (serType))

    def _SerCmd(self, serType:str, cmd:Cmd) -> str:
        """Serialize a command
        Args:
        - serType: [3 letter str] the name of the serializer
        - cmd: The command to serialize
        
        Returns:
        - cmdStr: The serialized command
        """
        try:
            return self.remoteCmdRxSerializers[serType].SerCmd(cmd)
        except KeyError:
            raise EOQ_ERROR_ACCESS_DENIED("Serializer %s is not allowed for sent commands" % (serType))




