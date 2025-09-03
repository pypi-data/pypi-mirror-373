""" Abstract class, base layer class for RPS Value object"""
from abc import abstractmethod
from typing import Optional
from pydantic import BaseModel
from Client.instance.rps_instance import RPSInstance
from Client.value.rps_value_error import RPSValueError


class IRPSValue(BaseModel):
    """ Abstract class, with minimal implementation of RPS Value properties
     and methods to implement

    Attributes:
        dependencies (dict): Represents additional depdencies that required to transform the RPS Value.
        instance (RPSInstance): Instance which contains Class name + Property Name.
        value (str): Raw value (protected / deprotected).
        error (RPSValueError): In case of error during transformation.

    Methods:
        add_dependecy(name: str, value: str): Add new dependency to dict of dependencies.
        remove_dependecy(name: str): Remove existing dependency from dict of dependencies.
    """
    instance: Optional[RPSInstance]
    error: Optional[RPSValueError] = None
    dependencies: Optional[dict] = {}

    @abstractmethod
    def add_dependecy(self, name: str, value: str) -> None:
        """Add new dependency into the dict of dependecies.

        Args:
            name (str): Name of new dependency
            value (str): Value of new dependency
        """

    @abstractmethod
    def remove_dependecy(self, name: str) -> None:
        """Remove dependency from dict of dependecies.

        Args:
            name (str): Name of dependency to remove
        """
