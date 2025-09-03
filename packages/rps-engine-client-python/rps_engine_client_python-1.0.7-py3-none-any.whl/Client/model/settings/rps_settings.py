from pydantic import BaseModel


class RPSSettings(BaseModel):
    """RPSSettings class represents the settings for the RPS (Remote Processing Service).
    Attributes:
        engineHostName (str): Host name of the RPS Engine API.
        identityServiceHostName (str): Host name of the Identity API.
        clientId (str): Client ID for accessing RPS services.
        clientSecret (str): Client Secret for accessing RPS services.
        timeout (int): Timeout in seconds for requests to the RPS services, default is 30 seconds.
    """
    engineHostName:str
    identityServiceHostName:str
    clientId:str
    clientSecret:str
    timeout:int = 30