""" Error class, which will represnt an error received from RPSEngine When performing Transform Request."""
class RPSEngineError(Exception):
    """Error received from Engine in Transformation process.

    Attributes: 
        message (str): Contains the text that describes the error.
        
    Args:
        Exception (_type_): Base class to inherit from 
    """
    message: str = None

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
