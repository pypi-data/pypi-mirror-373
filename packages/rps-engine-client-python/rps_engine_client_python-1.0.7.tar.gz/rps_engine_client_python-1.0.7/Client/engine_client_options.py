""""Client Options to configure accoring to the deployed RPS Engine API + Identity API"""
from datetime import timedelta
from Client.settings import Settings


class EngineClientOptions:
    """ Class represent the basis configuration of host names and keys to access RPS Platform services.

    Attributes:
        engine_host_name(str): Host name of RPS Engine API.
        identity_server_host_name(str): Host name of Identity API.
        api_key(str): API Key to access RPS Platform resources.
        secret_key(str): Secret Key to access RPS Platform resources.
        time_out(timeout): Seconds of interval between requests.
    """
    _default_time_out = timedelta(minutes=1)

    def __init__(self,
                 settings: Settings) -> None:
        """Initialize EngineClientOptions with the provided settings.
        Args:
            settings (Settings): Settings object containing configuration for RPS Engine and Identity API.
        """
        self.api_key = settings.rps.clientId
        self.secret_key = settings.rps.clientSecret
        self.engine_host_name = settings.rps.engineHostName
        self.identity_server_host_name = settings.rps.identityServiceHostName
        self.time_out = settings.rps.timeout if settings.rps.timeout else self._default_time_out