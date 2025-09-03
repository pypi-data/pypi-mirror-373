"""Evidence is the basis class at the core of the Context to use in Transform API"""
from pydantic import BaseModel


class Evidence(BaseModel):
    """Represent one evidence pair of Name and Value

    Attributes:
        name (str): The name property of the evidence
        value (str): The value property of the evidence
    """
    name: str
    value: str

    def __hash__(self):
        """Override __hash__ method, for custom comparison between evidences.

        Returns:
            int: Hash value of the evidence, used wen comparing evidences.
        """
        return ((hash(self._name) * 397) if self._name is not None else 0) ^ ((hash(self._value) * 397) if self._value is not None else 0)