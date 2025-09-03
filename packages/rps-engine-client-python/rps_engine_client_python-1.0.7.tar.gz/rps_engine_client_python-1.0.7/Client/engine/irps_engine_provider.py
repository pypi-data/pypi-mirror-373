"""The abstract class which includes the relevant methods to implement,
for providing the RPSEngine and the transformation request to the engine.
"""
from abc import ABC, abstractmethod
from Client.model.api.request.request_body import RequestBody
from Client.model.api.response.response_body import ResponseBody
from Client.auth_context import AuthContext


class IRPSEngineProvider(ABC):
    """ Abstract class which contains the method to implement in order to do a Transform request.
    
    Methods: 
        transform_async(request_body): Perform a Transform request to RPSEngine
    """

    @abstractmethod
    def transform_async(self,
                        *,
                        request_body: RequestBody,
                        auth_context: AuthContext = None) -> ResponseBody:
        """Perform a Transformation request to RPSEngine with requestBody as payload

        Args:
            request_body (RequestBody): The object contains the data for the Transform Request:
            RightsContext, ProcessingContext, Requests, LoggingContext
            auth_context (AuthContext, optional): The authentication context for the request. Defaults to None.

        Returns:
            ResponseBody: Response from RPSEngine with the transformed values.
        """