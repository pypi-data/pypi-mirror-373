"""Evidence is the basis class at the core of the Context"""
from pydantic import BaseModel


class Evidence(BaseModel):
    """Evidence class represents a pair of name and value.
    It is used to store information that can be used in various contexts, such as requests or responses.

    Attributes: 
        name (str): The name of the evidence.
        value (str): The value of the evidence.
    """
    name: str
    value: str

    """Represent one evidence pair of Name and Value

    Attributes:
        name (str): The name property of the evidence
        value (str): The value property of the evidence
    """

    def __hash__(self) -> int:
        """Override __hash__ method, for custom comparison between evidences.

        Returns:
            int: Hash value of the evidence, used wen comparing evidences.
        """
        return ((hash(self.name) * 397) if self.name is not None else 0) ^ ((hash(self.value) * 397) if self.value is not None else 0)
