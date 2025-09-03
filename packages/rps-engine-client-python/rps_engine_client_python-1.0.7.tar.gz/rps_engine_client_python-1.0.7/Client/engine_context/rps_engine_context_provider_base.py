""" Class represent a base functionality to get the contexts from an external source."""
from abc import abstractmethod
from Client.engine_context.irps_engine_context_provider import IRPSEngineContextProvider
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext


class RPSEngineContextProviderBase(IRPSEngineContextProvider):
    """Base class that represent the minimal functionality and abstract methods to 
        implement in all derived contextProviders

    Args:
        IRPSEngineContextProvider (IRPSEngineContextProvider): 
            Base class that contains abstract methods to implement

    Methods:
        initialize(): Initialize the Rights + Processing contexts dictionaries, depending on the external source.
        try_get_rights_context(context_key: str): Gets the matched Rights context, based on their name (key).
        try_get_processing_context(context_key: str): Gets the matched Processing context, based on their names.
    """
    
    def __init__(self):
        """Initialize an instance of the RPSEngineContextProviderBase class."""
        self.rights_contexts_by_key: dict[str, RightsContext] = None
        self.processing_contexts_by_key: dict[str, ProcessingContext] = None

    def initialize(self) -> None:
        """Initialize both dictionaries by getting the contexts,
            depending on implementation of derived classes.
        """
        self.rights_contexts_by_key = self._get_rights_contexts()
        self.processing_contexts_by_key = self._get_processing_contexts()

    def try_get_rights_context(self, context_key: str) -> RightsContext:
        """Gets the matched Rights context, based on their name (key).

        Args:
            context_key (str): name of Rights context to retrieve.

        Raises:
            ValueError: In case the Rights context dictionary does not exist.

        Returns:
            Rights context (Context): The retrieved Rights context
        """
        if self.rights_contexts_by_key is None:
            raise ValueError("Context provider is not initalized")

        evidences = self._get_evidences_from_context(
            self.rights_contexts_by_key.get(context_key))

        return RightsContext(evidences=evidences)

    def try_get_processing_context(self, context_key: str) -> ProcessingContext:
        """Gets the matched Processing context, based on their name (key).

        Args:
            context_key (str): name of Processing context to retrieve.

        Raises:
            ValueError: In case the Processing context dictionary does not exist.

        Returns:
            Processing context (Context): The retrieved Processing context
        """
        if self.processing_contexts_by_key is None:
            raise ValueError("Context provider is not initalized")

        evidences = self._get_evidences_from_context(
            self.processing_contexts_by_key.get(context_key))

        return ProcessingContext(evidences=evidences)

    @abstractmethod
    def _get_rights_contexts(self):
        # Getting the Rights context from external source.
        pass

    @abstractmethod
    def _get_processing_contexts(self):
        # Getting the Processing context from external source.
        pass

    @abstractmethod
    def _get_evidences_from_context(self, context):
        # Getting the evidences relevant for specific context, from the Context object.
        pass
