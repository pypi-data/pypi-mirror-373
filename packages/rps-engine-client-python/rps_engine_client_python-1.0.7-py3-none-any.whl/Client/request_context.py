"""Combine several requests into single call to RPS Engine API"""
from typing import Optional
from uuid import UUID
from Client.auth_context import AuthContext
from Client.context import Context
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.engine_context.rps_engine_context_resolver import RPSEngineContextResolver
from Client.value.irps_value import IRPSValue
from Client.request import Request


class RequestContext:
    """RequestContext class used to combine several Requests into single call.

    Attributes:
        request_by_guid(): Dictionary represents the all requests, by their ID's
        engine(): RPS Engine instance
        engine_context_resolver(): Engine context resolver, to get the contexts from.
        requests() : List of all requests included in the payload to RPS Engine.

    Methods:
        try_get_request(request_guid: uuid.UUID): Get request object by its unique identifier.
        transform(): Call RPS Engine in order to transform the request.
        transform_async(): Call RPS Engine in order to transform the request asynchronous.
        with_request_by_context_names(rps_values: list[IRPSValue],rights_context_name: str,processing_context_name: str, logging_context: Context = None):
            Get contexts object by their names, create the request object and add to list of requests.
        with_request(rps_values: list[IRPSValue], rights_context: Context, processing_context: ProcessingContext, logging_context: Context = None):
            Create the request object and add the request to list of requests.
    """
    def __init__(self,
                 engine: "RPSEngine",
                 context_resolver: RPSEngineContextResolver) -> None:
        """Initialize an instance of the class.

        Args:
            engine (RPSEngine): An instance of the RPS Engine class.
            context_resolver (RPSEngineContextResolver): Implementation of the RPSEngineContextResolver abstract class
        """
        self.engine: "RPSEngine" = engine
        self.engine_context_resolver: RPSEngineContextResolver = context_resolver
        self.request_by_guid: dict[UUID, Request] = dict()
        self.requests: list[Request] = self.request_by_guid.values()
        self.identifier: str = None
        self.auth_context: Optional[AuthContext] = None

    def try_get_request(self, request_guid: UUID) -> "Request":
        """Get request object by its unique identifier.
        Args:
            request_guid (uuid.UUID): Unique identifier of the request.
        Returns:
            Request: Request object if found, otherwise None.
        """
        return self.request_by_guid.get(request_guid)

    def transform(self) -> None:
        """Call RPS Engine in order to transform the request.
        Raises:
            ValueError: When the Engine context resolver is None.
        """
        return self.engine.transform(self)

    def transform_async(self) -> None:
        """Call RPS Engine in order to transform the request asynchronous.
        Raises:
            ValueError: When the Engine context resolver is None.
        """
        return self.engine.transform_async(request_context=self)

    def with_request_by_context_names(self,
                                  *,
                                  rps_values: list[IRPSValue],
                                  rights_context_name: str,
                                  processing_context_name: str,
                                  logging_context: Context = None,
                                  secrets_manager_id: UUID = None) -> 'RequestContext':
        """Get contexts object by their names, create the request object and add to list of requests.

        Args:
            rps_values (list[IRPSValue]): List of values included in the request.
            rights_context_name (str): Name of Rights context to find using the context resolver.
            processing_context_name (str):  Name of Processing context to find using the context resolver.
            logging_context (Context, optional): Logging context to include in the request. Defaults to None.
            secrets_manager_id (uuid.UUID, optional): The ID of the secrets manager to use for this request. Defaults to None.

        Raises:
            ValueError: When the Engine context resolver dont exist, cant get the contexts object.

        Returns:
            RequestContext: Self object, with new request added to requests property.
        """
        if self.engine_context_resolver is None:
            raise ValueError("Context resolver not found")

        contexts: tuple[RightsContext, ProcessingContext] = self.engine_context_resolver.resolve(
            rights_context_key=rights_context_name,
            processing_context_key=processing_context_name)

        return self.with_request(rps_values=rps_values,
                                rights_context=contexts[0],
                                processing_context=contexts[1],
                                logging_context=logging_context,
                                secrets_manager_id=secrets_manager_id)

    def with_request(self,
                    *,
                    rps_values: list[IRPSValue],
                    rights_context: RightsContext,
                    processing_context: ProcessingContext,
                    logging_context: Context = None,
                    secrets_manager_id: UUID = None) -> "RequestContext":
        """ Create the request object and add the request to list of requests.

        Args:
            rps_values (list[IRPSValue]): List of values included in the request.
            rights_context (Context): Name of Rights context to find using the context resolver.
            processing_context (Context):  Name of Processing context to find using the context resolver.
            logging_context (Context, optional): Logging context to include in the request. Defaults to None.
            secrets_manager_id (uuid.UUID, optional): The ID of the secrets manager to use for this request. Defaults to None.

        Returns:
             RequestContext: Self object, with new request added to requests property.
        """
        request = Request(values=rps_values,
                          rightsContext=rights_context,
                          processingContext=processing_context,
                          loggingContext=logging_context,
                          secretsManagerId=secrets_manager_id)

        self.request_by_guid[request.guid] = request

        return self
