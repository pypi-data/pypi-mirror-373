"""Simple example of usage of Protection and Deprotection of few RPSValues."""
from Client.engine.engine_factory import EngineFactory
from Client.instance.rps_instance import RPSInstance
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.evidence import Evidence
from Client.request_context import RequestContext
from Client.value.rps_value import RPSValue


class SimpleUsageExample:
    """Simple example of Protection and Deprotection and
     printing results from RPS Engine
    """
    __engine = EngineFactory.get_engine()

    if __name__ == "__main__":

        print('--- Example of simple protection and deprotection ---')

        # Manually creates admin rights context:
        admin_rights_context: RightsContext = \
            RightsContext(evidences=[Evidence(name='Role', value='Admin')])

        # Manually creates protect processing context:
        protect_processing_context: ProcessingContext = \
            ProcessingContext(evidences=[Evidence(name='Action', value='Protect')])

        # Manually creates deprotect processing context:
        deprotect_processing_context: ProcessingContext = \
            ProcessingContext(evidences=[Evidence(name='Action', value='Deprotect')])

        raw_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='Jonny')
        raw_last_name = RPSValue(instance=RPSInstance(className='User', propertyName='City'), originalValue='Silverhand')
        raw_birth_date = RPSValue(instance=RPSInstance(className='User', propertyName='Date'), originalValue='1998-11-16')

        protected_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='XXXXXXXXX')
        protected_last_name = RPSValue(instance=RPSInstance(className='User', propertyName='City'), originalValue='XXXXXXXXX')
        protected_birth_date = RPSValue(instance=RPSInstance(className='User', propertyName='Date'), originalValue='XXXXXXXXX')

        request_context: RequestContext = __engine.create_context()\
            .with_request(rps_values=[raw_first_name, raw_last_name, raw_birth_date],
                            rights_context=admin_rights_context,
                            processing_context=protect_processing_context)\
            .with_request(rps_values=[protected_first_name,
                            protected_last_name, protected_birth_date],
                            rights_context=admin_rights_context,
                            processing_context=deprotect_processing_context)

        request_context.transform_async()

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