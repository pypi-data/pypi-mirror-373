"""RPS Values Base class, second layer class for RPS Value object"""
from Client.value.irps_value import IRPSValue

class RPSValueBase(IRPSValue):
    """Class with implementation of RPS Value properties
     and implementing derived method from base class.
     
    Attributes:
        dependencies (dict): Dictionary of dependencies for the RPS Value.

    Inherited Attributes:   
        instance (RPSInstance): Instance of the RPS Instance.
        original (str): Original value of the RPS Value.
        transformed (str): Transformed value of the RPS Value.
        error (RPSValueError): Error object if any error occurred during transformation.

    Methods:
        add_dependency_range(dependencies: dict): Add new dependencies to instance dependencies.
        add_dependecy(name: str, value: str): Add new dependency to dict of dependencies.
        remove_dependecy(name: str): Remove existing dependency from dict of dependencies.
    """
 
    def add_dependecy(self, name: str, value: str) -> None:
        """Add a new dependency to the RPS Value.
        Args:
            name (str): Name of the dependency to add.
            value (str): Value of the dependency to add.
        """
        self.dependencies[name] = value

    def add_dependency_range(self, dependencies: dict = None) -> None:
        """Assign all dependencies from dictionary to instance's dependency.

        Args:
            dependencies (dict): Dictionary of dependencies to add to RPS Value.
        """
        if dependencies is None:
            return
        for key, value in dependencies.items():
            self.add_dependecy(key, value)

    def remove_dependecy(self, name: str) -> None:
        """Remove an existing dependency from the RPS Value.
        Args:
            name (str): Name of the dependency to remove.
        """
        self.dependencies.pop(name)