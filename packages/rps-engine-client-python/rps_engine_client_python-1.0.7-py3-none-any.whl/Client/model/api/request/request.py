"""Request model to send into Transform API in order to transform"""
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from Client.model.api.context.context import Context
from Client.model.api.instance import Instance


class Request(BaseModel):
    """Represent a single request object included in the call to RPS Engine.
    
    Attributes:
        guid (UUID): Unique identifier of the request.
        rights_context (UUID): Unique identifier of Rights context of the request to transform the data.
        processing_context (UUID): Unique identifier of Processing context defines how the values will be processed.
        logging_context (Context): Logging context defines data added to the audit logs that are generated for each request of transformation.
        secrets_manager (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        instances (list[Instance]): List of Instances to send for transformation for this request.    
    
    Methods:
        to_json():
    """
    guid: uuid.UUID = Field(default_factory=uuid.uuid4, alias="guid")
    rights_context: uuid.UUID = Field(..., alias="rightsContext")
    processing_context: uuid.UUID = Field(..., alias="processingContext")
    logging_context: Optional[Context] = Field(default=None, alias="loggingContext")
    secrets_manager: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, alias="secretsManager")
    instances: Optional[list[Instance]] = Field(default=list(), alias="instances")

    model_config = ConfigDict(
        json_encoders={uuid.UUID: lambda v: str(v)}
    )