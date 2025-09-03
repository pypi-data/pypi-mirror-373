""" Receive Rights + Processing Contexts from Json files."""
from typing import Any
from Client.context import Context
from Client.engine_context.rps_engine_context_provider_base import RPSEngineContextProviderBase
from Client.evidence import Evidence
from Client.extensions.json_extensions import get_json_from_file


class RPSEngineContextJsonFileProvider(RPSEngineContextProviderBase):
    """Class responsible to get the Rights context and Processing context from Json files 
    and implementing the derived methods from base class.
    
    Args:
        RPSEngineContextProviderBase (RPSEngineContextProviderBase):
            Base class with methods to implement.
    """

    def __init__(self,
                 rights_contexts_file_path: str,
                 processing_contexts_file_path: str) -> None:
        """Initialize an instance of the RPSEngineContextJsonFileProvider class.

        Args:
            rights_contexts_file_path (str): Path to Rights context json file.
            processing_contexts_file_path (str): Path to Processing context json file.
        """
        super().__init__()
        self.rights_contexts_file_path: str = rights_contexts_file_path
        self.processing_contexts_file_path: str = processing_contexts_file_path

    def _get_rights_contexts(self) -> Any:
        """Implementation of getting Rights context json object from file."""
        return get_json_from_file(self.rights_contexts_file_path)

    def _get_processing_contexts(self) -> Any:
        """Implementation of getting Processing context json object from file."""
        return get_json_from_file(self.processing_contexts_file_path)

    def _get_evidences_from_context(self, context) -> list[Evidence]:
        """Get evidences from context."""
        evidences = list()
        context_obj: Context = Context(**context)

        for context_evidence in context_obj.evidences:
            evidence = Evidence(name=context_evidence.name,
                                value=context_evidence.value)
            
            evidences.append(evidence)
        return evidences
