"""Client to interact with RPSEngine using REST API call in order to Transform request."""
from datetime import timedelta
import requests
from Client.auth_context import AuthContext
from Client.auth.itoken_provider import ITokenProvider
from Client.engine_client_options import EngineClientOptions
from Client.engine.irps_engine_provider import IRPSEngineProvider
from Client.model.api.request.request_body import RequestBody
from Client.model.api.response.response_body import ResponseBody


def default(obj):
    """Serialize to object to json.

    Args:
        obj (object): Object to serialize into Json for request to Engine.

    Raises:
        TypeError: Will be raised if object do not have to_json metod.

    Returns:
        json: Object with all properties serialized into complex json object.
    """
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


class EngineJsonRestApiClient(IRPSEngineProvider):
    """Class to call RPS Engine API using REST API calls in order to transform data.

    Attributes:
        host_name (str): Host name of RPS Engine API.
        time_out(str): Time out between requests that will determine if new request for token required.
        token_provider(ITokenProvider): Implementation of TokenProvider abstract class, to gain access to RPS Engine API resource.

    Methods:
        transform_async (request_body: RequestBody): 
            Request to gain access token and then Transform request to RPS Engine API.

    Args:
        IRPSEngineProvider (IRPSEngineProvider): Abstract base class to implement derived methods.
    """

    def __init__(self,
                 client_options: EngineClientOptions,
                 token_provider: ITokenProvider) -> None:
        """Initialize instance of class to interact with Engine API in REST API calls

        Args:
            client_options (EngineClientOptions): Client data required to interact with RPS Engine API.
            token_provider (ITokenProvider): Implementation of Token Provider,
                which responsible to gain token to access RPS Engine resource.
        """
        self.host_name: str = client_options.engine_host_name
        self.time_out: timedelta = client_options.time_out
        self.token_provider: ITokenProvider = token_provider

    def transform_async(self,
                        *,
                        request_body: RequestBody,
                        auth_context: AuthContext = None) -> ResponseBody:
        """ Implementation of abstract method.
            Perform the request to Identity server to get access token,
            perform Transform request to RPS Engine API.

        Args:
            request_body (RequestBody): Request object, to send to RPS Engine API.

        Returns:
            ResponseBody: Response object from RPS Engine API.
        """

        url: str = f'{self.host_name}api/transform'

        if self.token_provider is not None:
            access_token = self.token_provider.get_current_async()

            request_headers = {"Authorization": f"Bearer {access_token}",
                               "Content-Type": "application/json"}

            response = requests.post(url=url,
                                     data=request_body.model_dump_json(by_alias=True),
                                     headers=request_headers,
                                     timeout=self.time_out,
                                     verify=True)

        else:
            response = requests.post(url=url,
                                     data=request_body.model_dump_json(by_alias=True),
                                     headers={"Content-Type": "application/json"},
                                     timeout=self.time_out,
                                     verify=True)

        response.raise_for_status()

        response_body = ResponseBody().from_json(response.json())

        return response_body
