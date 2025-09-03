""" The abstract class which includes the relevant methods to implement,
 in order to get the contexts from external source.
"""
from abc import ABC, abstractmethod
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext


class IRPSEngineContextProvider(ABC):
    """Astract class which contains all methods to implement, in order to get the contexts from external source.
    
    Methods:
        initialize(): Abstract method to initialize the contexts dictionaries.
        try_get_rights_context(context_key: str): Abstract method, that gets the matched Rights context, based on key.
        try_get_processing_context(context_key: str): Abstract method, that gets the matched Processing context, based on key.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize class and non-public attributes."""

    @abstractmethod
    def try_get_rights_context(self, context_key: str) -> RightsContext:
        """Get Rights context object, using their name (key).

        Args:
            context_key (str): Name of Rights context to get from the dictionary (built by the external source).
        """

    @abstractmethod
    def try_get_processing_context(self, context_key: str) -> ProcessingContext:
        """Get Processing context object, using their name (key).

        Args:
            context_key (str): Name of Processing context to get from the dictionary (built by the external source).
        """
