"""Payload of Transform API Response after Transformation request."""
from uuid import UUID
from pydantic import BaseModel
from Client.model.api.error.error import Error
from Client.model.api.instance import Instance
from Client.model.api.response.response import Response
from Client.model.api.rps_value_error import RPSValueError


class ResponseBody(BaseModel):
    """The body of the response, received from Transform API as part of the transformation process

    Attributes:
        responses (): List of all responses, that related to all the requests sent to RPS Engine.
        error (): Error instance in case of the Transform API returned an error from RPS Engine.

    Methods:
        from_json(json: dict): Convert the json object received from Transform API into ResponseBody object
        create_responses(json_responses: list): Create list of response objects from the Transform API response.
        create_error(json_error: dict): Create an error object from the response received from Transform API.
        deserialize_instances_from_response(json_instances: list): Deserialize all instances into objects, from each json response.
    """
    responses: list[Response] = None
    error: Error = None

    def from_json(self, json: dict) -> "ResponseBody":
        """Convert the json object received from Transform API into ResponseBody object

        Args:
            json (dict): The response json object from Transform API.

        Returns:
            ResponseBody: New instance, created by the response json object.
        """
        if "responses" in json:
            self.responses = self.create_responses(json["responses"])

        if "error" in json:
            self.error = self.create_error(json["error"])

        return self

    def create_responses(self, json_responses: list) -> list[Response]:
        """Create list of response objects from the Transform API response.

        Args:
            json_responses (list): List of json responses received from Transform API.

        Returns:
            list[Response]: List of responses objects, created from the json response.
        """
        responses = list()

        for json_response in json_responses:

            request_id = UUID(json_response["request"])
            rights_context_id = UUID(json_response["rightsContext"])
            processing_context_id = UUID(json_response["processingContext"])

            response = Response(request=request_id,
                                rights_context=rights_context_id,
                                processing_context=processing_context_id,
                                instances=self.deserialize_instances_from_response(
                                json_response["instances"]))

            responses.append(response)

        return responses

    def create_error(self, json_error: dict) -> Error:
        """Create an error object from the response received from Transform API.

        Args:
            json_error (dict): Json object, represent the response from Transform API.
        """
        return Error(code=json_error["code"], message=json_error["message"])

    def deserialize_instances_from_response(self, json_instances: list[Instance]) -> list[Instance]:
        """Deserialize all instances into objects, from each json response.

        Args:
            json_instances (list): List of instances that sent to Transform API as part of a single request.

        Returns:
            list[Instance]: List of instances object with the processed values from Transform API.
        """
        instances = list()

        for json_instance in json_instances:
            class_name: str = json_instance["className"]
            property_name: str = json_instance["propertyName"]
            value: str = json_instance["value"]

            instance = Instance()
            instance.class_name = class_name
            instance.property_name = property_name
            instance.value = value

            if "error" in json_instance:
                error = json_instance["error"]

                if error is not None:
                    instance.error = RPSValueError(code=UUID(error["code"]), message=error["message"])

            instances.append(instance)

        return instances