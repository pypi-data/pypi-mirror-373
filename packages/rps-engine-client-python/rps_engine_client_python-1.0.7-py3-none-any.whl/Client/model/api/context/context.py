"""context model to use with Transform API"""
import uuid
from pydantic import BaseModel


class Context(BaseModel):
    """Represent base class of Rights + Processing + Logging contexts. 
    
    Attributes:
        guid (uuid): Unique identifier of the context.
        evidences (list): List of evidences object that belong to the context.

    Methods:
        to_json(): Custom serialization of the context object.
    """
    guid: uuid.UUID = uuid.uuid4()
    evidences: list = []