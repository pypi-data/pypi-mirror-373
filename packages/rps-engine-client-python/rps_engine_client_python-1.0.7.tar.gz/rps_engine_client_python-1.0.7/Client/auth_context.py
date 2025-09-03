"""AuthContext class for managing authentication context in a client application."""
from typing import Optional
from pydantic import BaseModel, Field


class AuthContext(BaseModel):
    """
    Represents authentication context with bearer token and client name.

    Attributes:
        bearer_token (str): The bearer token used for authentication.
        client_name (str): The name of the client associated with the authentication context.
    """
    bearer_token: Optional[str] = Field(..., alias="bearerToken")
    client_name: Optional[str] = Field(..., alias="clientName")