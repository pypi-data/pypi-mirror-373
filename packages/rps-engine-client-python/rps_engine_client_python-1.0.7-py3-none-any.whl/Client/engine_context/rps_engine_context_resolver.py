"""Get the Context objects from an external file, by using their names."""
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.engine_context.irps_engine_context_provider import IRPSEngineContextProvider


class RPSEngineContextResolver:
    """ Class which will be used to get the evidences of
     Rights + Processing context which are provided in an external files.
    
    Methods:
        resolve(rights_context_key: str, processing_context_key: str):
            Get the Context objects. by using the keys of each context.
    """

    def __init__(self, context_provider: IRPSEngineContextProvider) -> None:
        """Initialize class intance in order to get Context objects.

        Args:
            context_provider (IRPSEngineContextProvider): Implementation of the IRPSEngineContextProvider abstract class,
                which will be used to get the contexts from an external file.
        """
        self.context_provider: IRPSEngineContextProvider = context_provider

    def resolve(self,
                *,
                rights_context_key: str,
                processing_context_key: str) -> tuple[RightsContext, ProcessingContext]:
        """Using the Rights + Processing contexts keys, returns from the contextProvider the Rights + Processing contexts 

        Args:
            rights_context_key (str): Rights context name, which exist in the external file.
            processing_context_key (str): Processing context name, which exist in the external file.

        Raises:
            ValueError: In case one of the contexts doesnt exist in the external file.

        Returns:
            Tuple (RightsContext, ProcessingContext): Made of context objects
        """

        self.context_provider.initialize()

        rights_context: RightsContext = self.context_provider.try_get_rights_context(
            rights_context_key)
        if rights_context is None:
            raise ValueError(
                f"Rights Contexts = {rights_context_key} not found")

        processing_context: ProcessingContext = self.context_provider.try_get_processing_context(
            processing_context_key)
        if processing_context is None:
            raise ValueError(
                f"Processing Contexts = {processing_context_key} not found")

        return (rights_context, processing_context)
