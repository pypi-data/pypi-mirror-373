"""Error that could rise when transforming a single RPSValue"""
import uuid
from pydantic import BaseModel


class RPSValueError(BaseModel):
    """Class to represent the error from the transformation process.
    
    Attributes:
        code (uuid): Unique identifier of error .
        message (str): Description of the error.
    """
    code: uuid.UUID
    message: str