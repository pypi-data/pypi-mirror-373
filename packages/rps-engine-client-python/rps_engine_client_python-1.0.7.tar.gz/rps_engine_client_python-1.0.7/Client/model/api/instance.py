"""The data instance is send to Transform API to be processed"""
from typing import Optional
from pydantic import BaseModel, Field
from Client.model.api.context.context import Context
from Client.model.api.rps_value_error import RPSValueError


class Instance(BaseModel):
    """Class represents the value the client sends to the Transform API in order to process it.
    
    Attributes:
        logging_context(): The logging context defines data added to the audit logs that are generated for each request of transformation
        dependency_context(): Dependencies relevant to the instance in order to process it in RPS Engine.
        class_name(): Class Name of the instance
        property_name(): Property Name of the instance
        value(): Value of the instance
        error(): Error of the instance, if occured in Transform API during processing.
    """

    class_name: Optional[str]= Field(default=None, alias="className")
    property_name: Optional[str] = Field(default=None, alias="propertyName")
    value: Optional[str] = Field(default=None, alias="value")
    error: Optional[RPSValueError] = Field(default=None, alias="error", exclude_none=True)
    logging_context: Optional[Context] = Field(default=None, alias="loggingContext", exclude_none=True)
    dependency_context: Optional[Context] = Field(default=None, alias="dependencyContext", exclude_none=True)