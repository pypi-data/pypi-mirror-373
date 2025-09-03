"""The module is an implementation of the TokenProvider interface,
which is responsible to get permission to access RPSPlatform services.
"""
from typing import Optional
import requests
from Client.auth.itoken_provider import ITokenProvider
from Client.engine_client_options import EngineClientOptions


class ClientCredentialsTokenProvider(ITokenProvider):
    """ Class responsible to get the access token to the RPS Platform services.

    Client Credentials Authentication is an essential OAuth 2.0 flow,
    for securing access to RPSPlatform resources.
    The class implements the necessary method to get the access token
    from the identity server and provide it to the necessary modules.

    Args:
        ITokenProvider: Interface that contains the relevant methods 
            for implementation to receive access to RPSPlatform resources. 

    Methods:
        get_current_async(): Return the current valid access token.

        request_new_async(): Requests new access token, due to expired time.

    """

    def __init__(self, client_options: EngineClientOptions) -> None:
        """ Iinitialize class instance

        Args:
            client_options (EngineClientOptions): a formatted object contains
                API key, Secret key, RPSEngine & IdentityServer host names.
        """
        self.client_options: EngineClientOptions = client_options
        self.current: Optional[str] = None

    def get_current_async(self) -> str:
        """ Return the current valid access token. 

        Returns:
            str: The access token
        """
        if self.current is None:
            self.current = self.request_new_async()
        return self.current

    def request_new_async(self) -> str:
        """Requests new access token, due to expired time.

        Returns:
            str: newly received access token from IdentityServer.
        """
        url: str = f'{self.client_options.identity_server_host_name}connect/token'

        response = requests.post(url=url,
                                 data=self._get_token_request(),
                                 timeout=self.client_options.time_out,
                                 verify=True)
        response.raise_for_status()
        response_body = response.json()
        return response_body["access_token"]

    def _get_token_request(self) -> dict:
        """Prepare the request body for the token request.

        Returns:
            dict: The request body for the token request.
        """
        return {
            'grant_type': 'client_credentials',
            'client_id': f'{self.client_options.api_key}',
            'client_secret': f'{self.client_options.secret_key}'
        }
