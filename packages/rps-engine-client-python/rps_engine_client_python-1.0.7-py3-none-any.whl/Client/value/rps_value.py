"""Final layer class for RPS Value object"""
from typing import Optional
from pydantic import Field, computed_field
from Client.value.rps_value_base import RPSValueBase


class RPSValue(RPSValueBase):
    """Class represent the full object of RPS Value.

    Args:
        RPSValueBase (RPSValueBase): Base class with full methods.
        IRPSValue (IRPSValue): Abstract class with methods to implement.
    """
    original: Optional[str] = Field(default=None, alias='originalValue')
    transformed: Optional[str] = Field(default=None, alias='transformedValue')

    @computed_field(alias='value')
    def value(self) -> Optional[str]:
        """Value of the RPS Value.
        Returns:
            str: Value of RPSValue, after any Transformation.
        """
        return self.original
    @value.setter
    def value(self, value) -> None:
        """Set the value of the RPS Value.
        Args:
            value (str): Value to set for the RPSValue.
        """
        self.transformed = value