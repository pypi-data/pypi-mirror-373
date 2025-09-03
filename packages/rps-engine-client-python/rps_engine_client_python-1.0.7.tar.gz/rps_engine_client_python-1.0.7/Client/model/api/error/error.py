"""Using Tranform API, an error may rise during transformation"""
import uuid
from pydantic import BaseModel

class Error(BaseModel):
    """Transform API Error could rise during transformation requests.
        The Error class will be returned in case of such error as part of the response.

    Attributes:
        code (UUID): Unique identifier of error received from Tranform API.
        message (str): Description of the error received from Tranform API.
    """
    code: uuid.UUID
    message: str