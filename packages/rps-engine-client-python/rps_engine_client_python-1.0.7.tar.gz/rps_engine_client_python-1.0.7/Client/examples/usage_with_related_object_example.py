"""Example of usage of Protection of RPSValues received from external file"""
import os
from Client.engine.engine_factory import EngineFactory
from Client.instance.rps_instance import RPSInstance
from Client.extensions.json_extensions import get_json_from_file
from Client.request_context import RequestContext
from Client.value.rps_value import RPSValue


class UsageWithRelatedObjectExample:
    """Example of Protection of RPSValues received from external file,
    and printing results from RPS Engine
    """
    __engine = EngineFactory.get_engine()
    
    __example_json_file_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..",
        "Examples", "Data", "ExampleOfJsonToProtect.json"
    )

    if __name__ == "__main__":

        print('--- Example of protection JSON file with related object ---')

        # Load json with data to protect:
        json_to_protect = get_json_from_file(os.path.abspath(__example_json_file_path))
        
        # Create RPS Values for request
        rps_values = list()
        for name, value in json_to_protect.items():
            rps_value = RPSValue(
                instance=RPSInstance(className="Person", propertyName=name),
                originalValue=value)

            rps_values.append(rps_value)

        # Protect Request
        request_context: RequestContext = __engine.create_context().with_request_by_context_names(
            rps_values=rps_values,
            rights_context_name="TransformRegTAX",
            processing_context_name="ProtectRegTAX")

        request_context.transform_async()

        print('--- Transformed Values ---')
        for rps_value in rps_values:
            print(f'{rps_value.instance.class_name}, {rps_value.instance.property_name}. Original: {rps_value.original}. Transformed: {rps_value.transformed}. {rps_value.error.message if rps_value.error else ""}')
