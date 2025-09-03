from enum import Enum

class ContextSource(Enum):
    """
    An enumeration representing the possible sources of context data.

    Attributes:
        JSON: Indicates that the context source is a JSON object.
        SETTINGS: Indicates that the context source is application settings.
    """
    JSON = "json"
    SETTINGS = "settings"