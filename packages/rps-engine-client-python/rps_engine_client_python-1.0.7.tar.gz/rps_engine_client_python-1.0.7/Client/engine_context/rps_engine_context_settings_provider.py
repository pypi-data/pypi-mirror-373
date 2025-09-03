from typing import Any
from Client.context import Context
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.engine_context.rps_engine_context_provider_base import RPSEngineContextProviderBase
from Client.evidence import Evidence


class RPSEngineContextSettingsProvider(RPSEngineContextProviderBase):
    """
    Provider for Rights and Processing contexts based on settings.
    This class retrieves rights and processing contexts from provided settings,
    allowing for dynamic configuration of contexts without hardcoding them.
    
    Attributes:
        rights_contexts_settings (dict[str, RightsContext]): Dictionary of rights contexts settings.
        processing_contexts_settings (dict[str, ProcessingContext]): Dictionary of processing contexts settings.
    """
    def __init__(self,
                 rights_contexts_settings: dict[str, RightsContext],
                 processing_contexts_settings: dict[str, ProcessingContext] ) -> None:
        super().__init__()
        self.rights_contexts_by_key: dict[str, RightsContext] = rights_contexts_settings
        self.processing_contexts_by_key: dict[str, ProcessingContext] = processing_contexts_settings

    def _get_rights_contexts(self) -> Any:
        """Get rights contexts from settings."""
        return self.rights_contexts_by_key
    
    def _get_processing_contexts(self) -> Any:
        """Get processing contexts from settings."""
        return self.processing_contexts_by_key
    
    def _get_evidences_from_context(self, context: Context) -> list[Evidence]:
        """Get evidences from context."""
        evidences = list()

        for context_evidence in context.evidences:
            evidence = Evidence(name=context_evidence.name,
                                value=context_evidence.value)
            
            evidences.append(evidence)
        return evidences
    