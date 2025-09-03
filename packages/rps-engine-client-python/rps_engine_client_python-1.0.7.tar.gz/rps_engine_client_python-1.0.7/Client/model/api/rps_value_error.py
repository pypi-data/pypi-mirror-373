"""Error that could rise when transforming a single RPSValue"""
import uuid
from pydantic import BaseModel


class RPSValueError(BaseModel):
    """Class to represent the error from the transformation process for each instance.
    
    Attributes:
        code (uuid): Unique identifier of error .
        message (str): Description of the error.

    Methods:
        create(self, guid: uuid.UUID, message: str)
    """
    code: uuid.UUID
    message: str

    def create(self, guid: uuid.UUID, message: str) -> 'RPSValueError':
        """Create a new instance of the class.

        Args:
            guid (uuid.UUID): Unique identifier of the error.
            message (str): Description of the error.

        Returns:
            _type_: _description_
        """
        return RPSValueError(guid=guid, message=message)
