"""Engine class, with all properties and methods related to The transformation process."""
import requests
from Client.auth_context import AuthContext
from Client.context import Context
from Client.engine.irps_engine_provider import IRPSEngineProvider
from Client.engine.rps_engine_converter import RPSEngineConverter
from Client.engine.rps_engine_exception import RPSEngineError
from Client.engine_context.rights_context import RightsContext
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rps_engine_context_resolver import RPSEngineContextResolver
from Client.model.api.request.request_body import RequestBody
from Client.model.api.response.response_body import ResponseBody
from Client.value.irps_value import IRPSValue
from Client.request_context import RequestContext


class RPSEngine:
    """The RPS Engine class.

    Attributes:
        provider (IRPSEngineProvider): Implementation of the the RPSEngineProvider abstract class
        converter (RPSEngineConverter): The converter conducts conversions between data types related to transformation requests/responses.
        engine_context_resolver (RPSEngineContextResolver): Class which receives the RightsContexts + ProcessingContexts.

    Methods:
        create_context(): Create an empty RequestContext instance.

        transform_with_context_names(rps_values: list[IRPSValue], rights_context_name: str, processing_context_name: str, logging_context: Context):
            Get context by their names, build request context and perform Transformation.

        transform_with_contexts(rps_values: list[IRPSValue], rights_context: Context, processing_context: ProcessingContext, logging_context: Context):
            Build request and perform Transformation. 

        transform(request_context: RequestContext):
            Perform Transformation with the given request.

        transform_async_with_context_names(rps_values: list[IRPSValue], rights_context_name: str, processing_context_name: str, logging_context: Context)::
            Asynchronous transform request to Engine with contexts by their names. 

        transform_async_with_contexts(rps_values: list[IRPSValue], rights_context: Context, processing_context: ProcessingContext, logging_context: Context):
            Asynchronous transform request to Engine with contexts.

        transform_async(request_context: RequestContext):
            Perform asynchronous Transformation with the given request.
    """

    def __init__(self,
                 engine_provider: IRPSEngineProvider,
                 converter: "RPSEngineConverter",
                 context_resolver: RPSEngineContextResolver) -> None:
        """Initialize Engine instance for Transformations.

        Args:
            engine_provider (IRPSEngineProvider): 
                Implementation of the the RPSEngineProvider interface.
            converter (RPSEngineConverter):             
                The converter, which conducts the conversions between different data types that are asocciated to transformation requests/responses.
            context_resolver (RPSEngineContextResolver):
                Class which receives the RightsContexts + ProcessingContexts from external source.
        """
        self.provider = engine_provider
        self.converter = converter
        self.engine_context_resolver = context_resolver

    def create_context(self,
                      identifier: str = None,
                      auth_context: AuthContext = None) -> RequestContext:
        """Returns an initialized RequestContext instance.

        Returns:
            RequestContext: RequestContext instance ready for use in Transformation request.
        """
        context: RequestContext = RequestContext(
            engine=self,
            context_resolver=self.engine_context_resolver)
        
        if identifier is not None:
            context.identifier = identifier

        if auth_context is not None:
            context.auth_context = auth_context

        return context

    def transform_with_context_names(self,
                                     *,
                                     rps_values: list[IRPSValue],
                                     rights_context_name: str,
                                     processing_context_name: str,
                                     logging_context: Context = None,
                                     auth_context: AuthContext = None,
                                     secrets_manager_id: str = None) -> None:
        """ Get context by their names, build request context and perform Transformation.

        Args:
            rps_values (list[IRPSValue]): List of values to transform with Engine.
            rights_context_name (str): Name of rights context that will be found using the resolver.
            processing_context_name (str): Name of processing context that will be found using the resolver.
            logging_context (Context): Data that will be added to the audit log that are generated for each request.
            auth_context (AuthContext): Authentication context for the request.
            secrets_manager_id (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        """
        self.transform_async_with_context_names(
            rps_values=rps_values,
            rights_context_name=rights_context_name,
            processing_context_name=processing_context_name,
            logging_context=logging_context,
            auth_context=auth_context,
            secrets_manager_id=secrets_manager_id
        )

    def transform_with_contexts(self,
                                *,
                                rps_values: list[IRPSValue],
                                rights_context: Context,
                                processing_context: ProcessingContext,
                                logging_context: Context = None,
                                auth_context: AuthContext = None,
                                secrets_manager_id: str = None) -> None:
        """Build request and perform Transformation. 

        Args:
            rps_values (list[IRPSValue]):  List of values to transform with Engine.
            rights_context (Context): Rights context object to use in request.
            processing_context (ProcessingContext): Processing context object to use in request.
            logging_context (Context): Data that will be added to the audit log that are generated for each request.
            auth_context (AuthContext): Authentication context for the request.
            secrets_manager_id (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        """
        self.transform_async_with_contexts(
            rps_values=rps_values,
            rights_context=rights_context,
            processing_context=processing_context,
            logging_context=logging_context,
            auth_context=auth_context,
            secrets_manager_id=secrets_manager_id
        )

    def transform(self, request_context: RequestContext) -> None:
        """Perform Transformation with the given request.

        Args:
            request_context (RequestContext): Request object, with RPSValues, RightsContext, ProcessingContext.
        """
        self.transform_async(request_context=request_context)

    def transform_async_with_context_names(self,
                                           *,
                                           rps_values: list[IRPSValue],
                                           rights_context_name: str,
                                           processing_context_name: str,
                                           logging_context: Context = None,
                                           auth_context: AuthContext = None,
                                           secrets_manager_id: str = None) -> None:
        """Asynchronous transform request to Engine with contexts by their names.

        Args:
            rps_values (list[IRPSValue]): List of values to transform with Engine.
            rights_context_name (str): Name of rights context that will be found using the resolver.
            processing_context_name (str): Name of processing context that will be found using the resolver.
            logging_context (Context): Data that will be added to the audit log that are generated for each request. Defaults to None.
            auth_context (AuthContext): Authentication context for the request.
            secrets_manager_id (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        Raises:
            ValueError: When resolver not exist and will not be able to get contexts by their names.
        """
        if self.engine_context_resolver is None:
            raise RPSEngineError("Context resolver not found")

        contexts: tuple[RightsContext, ProcessingContext] = self.engine_context_resolver.resolve(
            rights_context_key=rights_context_name,
            processing_context_key=processing_context_name)

        self.transform_async_with_contexts(
            rps_values=rps_values,
            rights_context=contexts[0],
            processing_context=contexts[1],
            logging_context=logging_context,
            auth_context=auth_context,
            secrets_manager_id=secrets_manager_id
        )

    def transform_async_with_contexts(self,
                                      *,
                                      rps_values: list[IRPSValue],
                                      rights_context: RightsContext,
                                      processing_context: ProcessingContext,
                                      logging_context: Context = None,
                                      auth_context: AuthContext = None,
                                      secrets_manager_id: str = None) -> None:
        """Asynchronous transform request to Engine with contexts.

        Args:
            rps_values (list[IRPSValue]):  List of values to transform with Engine.
            rights_context (Context): Rights context object to use in request.
            processing_context (ProcessingContext): Processing context object to use in request.
            logging_context (Context): Data that will be added to the audit log that are generated for each request.
            auth_context (AuthContext): Authentication context for the request.
            secrets_manager_id (UUID): The ID of the secrets manager to use for this request. Defaults to None.
        """
        context: RequestContext = self.create_context(auth_context=auth_context)
        self.transform_async(request_context= context.with_request(
            rps_values=rps_values,
            rights_context=rights_context,
            processing_context=processing_context,
            logging_context=logging_context,
            secrets_manager_id=secrets_manager_id
        ))

    def transform_async(self,
                        *,
                        request_context: RequestContext) -> None:
        """Perform asynchronous Transformation with the given request.

       Args:
            request_context (RequestContext): Request object, with RPSValues, RightsContext, ProcessingContext.

        Raises:
            error: When getting HTTP error during Tranform request.
        """
        request_body: RequestBody = self.converter.to_request_body(request_context=request_context)

        try:
            response_body: ResponseBody = self.provider.transform_async(request_body=request_body)
            self.converter.from_response_body(
                response_body=response_body, request_context=request_context)

        except requests.exceptions.HTTPError as error:
            self.converter.assign_none_values(request_context=request_context)
            raise RPSEngineError(error) from error
