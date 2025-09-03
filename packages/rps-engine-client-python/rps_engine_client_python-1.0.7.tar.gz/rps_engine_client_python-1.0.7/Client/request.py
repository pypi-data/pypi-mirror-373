"""Request model is the basis object to RPS Engine"""
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from Client.context import Context
from Client.engine_context.rights_context import RightsContext
from Client.engine_context.processing_context import ProcessingContext
from Client.value.irps_value import IRPSValue


class Request(BaseModel):
    """Represent a single request object created by client.
    
    Attributes:
        guid (UUID): Unique identifier of the request.
        values (list[IRPSValue]): List of RPS Values to send for transformation for this request.
        rights_context (Context): Rights of the request to transform the data.
        processing_context (ProcessingContext): Processing context defines how the values will be processed.
        logging_context (Context): Logging context defines data added to the audit logs that are generated for each request of transformation.
        secrets_manager_id (UUID): The ID of the secrets manager to use for this request. Defaults to None.
    """
    guid: uuid.UUID = Field(default_factory=uuid.uuid4, alias="guid")
    values: list[IRPSValue]
    rights_context: RightsContext = Field(..., alias="rightsContext")
    processing_context: ProcessingContext = Field(..., alias="processingContext")
    logging_context: Optional[Context] = Field(default=None, alias="loggingContext")
    secrets_manager_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, alias="secretsManagerId")

    model_config = ConfigDict(
        json_encoders={uuid.UUID: lambda v: str(v)}
    )
    