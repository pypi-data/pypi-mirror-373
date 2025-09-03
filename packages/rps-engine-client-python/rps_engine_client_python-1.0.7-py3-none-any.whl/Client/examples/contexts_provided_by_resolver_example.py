"""Example of usage of Protection and Deprotection of few RPSValues,
using the contexts name instead of objects"""
from Client.instance.rps_instance import RPSInstance
from Client.engine.engine_factory import EngineFactory
from Client.request_context import RequestContext
from Client.value.rps_value import RPSValue


class ContextsProvidedByResolverExample:
    """Example of Protection and Deprotection, using the contexts name instead of objects
    and printing results from RPS Engine
    """

    __engine = EngineFactory.get_engine()

    if __name__ == "__main__":

        print('--- Example with rights and processing contexts provided by abstract resolver ---')

        raw_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='Jonny')
        raw_last_name = RPSValue(instance=RPSInstance(className='User', propertyName='City'), originalValue='Silverhand')
        raw_birth_date = RPSValue(instance=RPSInstance(className='User', propertyName='Date'), originalValue='1998-11-16')

        protected_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='XXXXXXXX')
        protected_last_name = RPSValue(instance=RPSInstance(className='User', propertyName='City'), originalValue='XXXXXXXX')
        protected_birth_date = RPSValue(instance=RPSInstance(className='User', propertyName='Date'), originalValue='XXXXXXXX')

        # Protect Request
        protect_request_context: RequestContext = __engine.create_context().with_request_by_context_names(
            rps_values= [raw_first_name, raw_last_name, raw_birth_date],
            rights_context_name="Admin",
            processing_context_name="Protect")

        # Deprotect Request
        deprotect_request_context: RequestContext = __engine.create_context().with_request_by_context_names(
            rps_values= [protected_first_name, protected_last_name, protected_birth_date],
            rights_context_name="Admin",
            processing_context_name="Deprotect")

        protect_request_context.transform_async()
        deprotect_request_context.transform_async()

        print(
            f'Raw fist name. Original: {raw_first_name.original}. Transformed: {raw_first_name.transformed}')
        print(
            f'Raw last name. Original: {raw_last_name.original}. Transformed: {raw_last_name.transformed}')
        print(
            f'Raw birth date. Original: {raw_birth_date.original}. Transformed: {raw_birth_date.transformed}')
        print(
            f'Protected fist name. Original: {protected_first_name.original}. Transformed: {protected_first_name.transformed}')
        print(
            f'Protected last name. Original: {protected_last_name.original}. Transformed: {protected_last_name.transformed}')
        print(
            f'Protected birth date. Original: {protected_birth_date.original}. Transformed: {protected_birth_date.transformed}')
