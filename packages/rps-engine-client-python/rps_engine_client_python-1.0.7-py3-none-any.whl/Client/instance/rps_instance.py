"""RPS Instance module"""
from pydantic import BaseModel, Field


class RPSInstance(BaseModel):
    """ Class represents Instance to transform in RPS Engine.
        Pair of class and property defines one data instance

    Attributes:
        class_name (str): The class name of the instance.
        property_name (str): The property name of the instance.
    """
    class_name: str = Field(..., alias='className')
    property_name: str = Field(..., alias='propertyName')