"""Payload to Transform API in Transformation request."""
from typing import Optional
from pydantic import BaseModel, Field
from Client.model.api.context.context import Context
from Client.model.api.request.request import Request


class RequestBody(BaseModel):
    """The body of the request to send to Transform API as part of the transformation process

    Attributes:
        logging_context: Logging context defines data added to the audit logs that are generated for each request to Transform API.
        rights_contexts: List of rights contexts that are included in all requests.
        processing_contexts: List of processing contexts that are included in all requests.
        requests: List of all the requests to send to RPS Engine

    Methods:
        to_json(): Custom json serialization of the class instances.
    """
    logging_context: Optional[Context] = Field(None, alias='loggingContext')
    rights_contexts: list[Context] = Field(default=list(), alias='rightsContexts')
    processing_contexts: list[Context] = Field(default=list(), alias='processingContexts')
    requests: list[Request] = Field(default=list(), alias='requests')