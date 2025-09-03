"""Base class for Rights + Processing + Logging contexts."""
from pydantic import BaseModel
from Client.evidence import Evidence


class Context(BaseModel):
    """Represent base class of Rights + Processing + Logging contexts. 
    All of them are lists of Evidence.
    
    Attributes:
        evidences (list): List of evidences object that belong to the context.
    """
    evidences: list[Evidence]