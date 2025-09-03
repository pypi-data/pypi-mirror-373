"""A module responsible to convert types of object into others.
    Consumed when building a request to RPSEngine 
    and when parsing a response from RPSEngine 
"""
import uuid
from Client.context import Context
from Client.engine.rps_engine_exception import RPSEngineError
from Client.extensions.context_extensions import to_context
from Client.model.api.context.context import Context as ApiContext
from Client.model.api.context.evidence import Evidence as ApiEvidence
from Client.model.api.instance import Instance
from Client.model.api.request.request import Request as ApiRequest
from Client.model.api.request.request_body import RequestBody
from Client.model.api.response.response_body import ResponseBody
from Client.request import Request
from Client.request_context import RequestContext
from Client.value.rps_value_error import RPSValueError
from Client.value.irps_value import IRPSValue


class RPSEngineConverter:
    """Class that will be used in order to perform conversions between classes 
    in different points in process of transformations.

    Methods:
        to_request_body(request_context): Construct object to send to RPSEngine

        from_response_body(response_body, request_context): Parse response from RPS Engine and modify RPS Values
        
        assign_none_values(request_context): Assign None to all RPSValues in all requests

        to_request(rps_values, request_guid, rights_context_guid, processing_context_guid, logging_context = None):
            Create Request object base on all parts
        
        to_model(context): Model context object 
    """

    def to_request_body(self,
                        *,
                        request_context: "RequestContext") -> RequestBody:
        """Construct the object to send to the RPSEngine by the object received from client. 

        Args:
            request_context (RequestContext): Request object built by the client.
            Includes RPSValues, RightsContext, ProcessingContext, LoggingContext  

        Returns:
            RequestBody: The object that will be sent to RPSEngine,
            built from the object received from client
        """
        request_body = RequestBody()

        if len(request_context.requests) == 0:
            return request_body

        rights_contexts_by_guid: dict[uuid.UUID, ApiContext] = dict()
        processing_contexts_by_guid: dict[uuid.UUID, ApiContext] = dict()

        for request in request_context.requests:

            if len(request.values) == 0:
                continue

            rights_context: ApiContext = self.to_model(context=request.rights_context)

            if rights_context.guid not in rights_contexts_by_guid:
                rights_context_guid = uuid.uuid4()
                rights_context.guid = rights_context_guid

                rights_contexts_by_guid[rights_context_guid] = rights_context
                request_body.rights_contexts.append(rights_context)

            processing_context: ApiContext = self.to_model(context=request.processing_context)
            logging_context: ApiContext = self.to_model(context=request.logging_context)

            if processing_context is None:
                request_body.requests.append(
                    self.to_request(rps_values=request.values,
                                   request_guid=request.guid,
                                   rights_context_guid=rights_context_guid,
                                   processing_context_guid=None,
                                   logging_context=logging_context,
                                   secrets_manager_id=request.secrets_manager))
                continue

            if processing_context.guid not in processing_contexts_by_guid:
                processing_context_guid = uuid.uuid4()
                processing_context.guid = processing_context_guid

                processing_contexts_by_guid[processing_context_guid] = processing_context
                request_body.processing_contexts.append(processing_context)

            request_body.requests.append(
                self.to_request(rps_values=request.values,
                               request_guid=request.guid,
                               rights_context_guid=rights_context_guid,
                               processing_context_guid=processing_context_guid,
                               logging_context=logging_context))

        return request_body

    def from_response_body(self,
                           *,
                            response_body: ResponseBody,
                            request_context: "RequestContext") -> None:
        """Parse the response received from RPSEngine and
        modify request_context with TransformedValues

        Args:
            response_body (ResponseBody): Response received from RPSEngine
            request_context (RequestContext): The original Request object built by client.

        Raises:
            RPSEngineError: Error while be raised if receive error 
            from RPSEngine while Transform request
        """
        if hasattr(response_body, "error") and response_body.error is not None:
            raise RPSEngineError("Error received from RPS Engine API response." +
                                     f"Code: '{response_body.error.code}'. " +
                                     f"Message: '{response_body.error.message}')")

        for response in response_body.responses:
            request: Request = request_context.try_get_request(response.request)
            if request is None:
                continue

            for i, response_instance in enumerate(response.instances):
                request.values[i].value = response_instance.value

                if response_instance.error is not None:
                    request.values[i].error = RPSValueError(
                        code=response_instance.error.code,
                        message=response_instance.error.message)

    def assign_none_values(self, *, request_context: "RequestContext") -> None:
        """Assign to all RPSValues in each request None values

        Args:
            request_context (RequestContext): Object contains all requests object
        """
        for request in request_context.requests:
            for rps_value in request.values:
                rps_value.value = None

    def to_request(self,
                   *,
                  rps_values: list[IRPSValue],
                  request_guid: uuid.UUID,
                  rights_context_guid: uuid.UUID,
                  processing_context_guid: uuid.UUID,
                  logging_context: ApiContext = None,
                  secrets_manager_id: uuid.UUID = None):
        """Create Request object base on all of its parts

        Args:
            rps_values (list[IRPSValue]): List of all values to transform in RPSEngine.
            request_guid (uuid.UUID): Unique identifier of the request
            rights_context_guid (uuid.UUID): Unique identifier of RightsContext
            processing_context_guid (uuid.UUID): Unique identifier of ProcessingContext
            logging_context (ApiContext, optional): Logging object for request. Defaults to None.
            secrets_manager_id (uuid.UUID, optional): The ID of the secrets manager to use for this request. Defaults to None.

        Returns:
            ApiRequest: Built Request object, contains all parts for Transform request.
        """
        request: ApiRequest = ApiRequest(guid=request_guid,
                                         rightsContext=rights_context_guid,
                                         processingContext=processing_context_guid,
                                         loggingContext=logging_context,
                                         secretsManager=secrets_manager_id)
        for rps_value in rps_values:
            instance = Instance()
            instance.value = rps_value.value
            request.instances.append(instance)

            if rps_value.instance is not None:
                instance.class_name = rps_value.instance.class_name
                instance.property_name = rps_value.instance.property_name

            if len(rps_value.dependencies) > 0:
                instance.dependency_context = to_context(dictionary=rps_value.dependencies)

        return request

    def to_model(self, *, context: Context) -> ApiContext:
        """Convert context Object to a model understood by RPSEngine.

        Args:
            context (Context): Object contains evidences, 
            represents base class for RightsContext, ProcessingContext, LoggingContext

        Returns:
            ApiContext: Context object with ID and evidences, understood by RPSEngine.
        """
        if context is None:
            return None

        model_context = ApiContext()
        evidences = list()

        for evidence in context.evidences:
            model_evidence = ApiEvidence(name=evidence.name, value=evidence.value)
            evidences.append(model_evidence)

        model_context.evidences = evidences
        return model_context
