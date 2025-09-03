from pydantic import BaseModel


class FilesSettings(BaseModel):
    """Settings for file paths used in the Client library.
    Attributes:
        rightsContextsFilePath (str): Path to the file containing rights contexts.
        processingContextsFilePath (str): Path to the file containing processing contexts.
    """
    rightsContextsFilePath: str = None
    processingContextsFilePath: str = None
