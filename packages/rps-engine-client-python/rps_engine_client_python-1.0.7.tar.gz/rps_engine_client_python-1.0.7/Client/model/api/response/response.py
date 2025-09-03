"""Response model received from Transform API after transformation"""
import uuid
from pydantic import BaseModel, ConfigDict, Field
from Client.model.api.instance import Instance


class Response(BaseModel):
    """Represent a single response object received from RPS Engine.

    Attributes:
        request(UUID): Unique identifier of the specific request that this response it related to.
        rights_context (UUID): Unique identifier of Rights context relevant for the specific request.
        processing_context (UUID): Unique identifier of Processing context relevant for the specific request.
        secrets_manager (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        instances (list[Instance]): List of Instances that were sent to RPS Engine, after transformation.    
    """
    request: uuid.UUID = Field(default_factory=uuid.uuid4, alias='request')
    rights_context: uuid.UUID = Field(default_factory=uuid.uuid4, alias='rightsContext')
    processing_context: uuid.UUID = Field(default_factory=uuid.uuid4, alias='processingContext')
    secrets_manager: uuid.UUID = Field(default_factory=uuid.uuid4, alias='secretsManager')
    instances: list[Instance] = Field(..., alias='instances')

    model_config = ConfigDict(
        json_encoders={uuid.UUID: lambda v: str(v)}
    )