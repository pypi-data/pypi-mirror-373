"""
 Domain

 Bjoern Annighoefer 2021
"""
from ..query import Qry, Obj
from ..domain import Domain
from ..config import Config
from abc import ABC, abstractmethod


class DomainConnector(ABC):
    """ Base class for every domain connector
    A domain connector is a class that connects to a domain and interacts with it.
    The domain connector will interact as long as it is connected to the domain.
    """
    config:Config = None
    domain:Domain = None
    sessionId:str = None
    isConnected:bool = False

    def __init__(self, config:Config):
        """
        Initializes the domain connector with a configuration.

        ```text
        ___________________       ___________________
        | DomainConnector |       | Domain          |
        |-----------------|       |-----------------|
                | init
                X----
                X    |
                X<---
                |
                | Connect
                X----------------------->
        ```

        :param Config config: The eoq3 configuration structure
        """
        self.config = config

    @abstractmethod
    def Connect(self,domain:Domain, sessionId:str=None)->None:
        """ Connects and synchronizes with a domain.
        Will stay connected until Disconnect is called.

        Args:
        - domain: The domain to connect to
        - sessionId: The session id to use for the connection. If None, no session id will be used.
        """
        self.domain = domain
        self.sessionId = sessionId

    def IsConnected(self)->bool:
        """ Returns true if the domain connector is connected to the domain
        """
        return self.isConnected

    def SetConnected(self, isConnected:bool=True)->None:
        """ Sets the connection status of the domain connector
        """
        self.isConnected = isConnected

    def Disconnect(self)->None:
        """Disconnects the domain connector from the domain
        """
        self.domain = None
        self.sessionId = None
        self.isConnected = False

    def Close(self)->None:
        """Gracefully shutting down and cleaning the domain connector.
        If the domain connector is connected to a domain, it will be disconnected.
        """
        if(self.isConnected):
            self.Disconnect()
