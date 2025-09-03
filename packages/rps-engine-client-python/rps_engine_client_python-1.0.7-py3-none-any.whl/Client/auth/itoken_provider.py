"""The abstract class which includes the relevant methods to implement,
in order to get the access token from IdentityServer. 
"""
from abc import ABC, abstractmethod


class ITokenProvider(ABC):
    """ Abstract class which contains the method to implement in order to gain the token.
    
    Methods:
        get_current_async(): Get the current valid access token
        
        request_new_async(): Request new access token from Identity Server, when timeout passed
    """
    @abstractmethod
    def get_current_async(self) -> str:
        """ Get the current valid access token"""

    @abstractmethod
    def request_new_async(self) -> str:
        """ Request new access token from Identity Server, when timeout passed"""
