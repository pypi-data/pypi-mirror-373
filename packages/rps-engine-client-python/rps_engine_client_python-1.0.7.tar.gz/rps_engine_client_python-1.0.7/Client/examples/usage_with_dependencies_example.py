"""Example of usage of Protection of RPSValues with Dependencies"""
from Client.instance.rps_instance import RPSInstance
from Client.engine.engine_factory import EngineFactory
from Client.value.rps_value import RPSValue


class UsageWithDependenciesExample:
    """Example of Protection of RPSValues with Dependencies,
    and printing results  from RPS Engine"""

    __engine = EngineFactory.get_engine()

    if __name__ == "__main__":

        print('--- Example of protection with dependencies ---')

        # Create RPS Value with dependency
        payment_date = RPSValue(instance=RPSInstance(className='Payment', propertyName='Date'),
                                originalValue='02.11.2021',
                                dependencies={
            "min": "01.10.2021",
            "max": "02.11.2021"
        })

        # Create ordinary RPSValue
        payment_amount = RPSValue(instance=RPSInstance(className='Payment', propertyName='Amount'), originalValue='999')

        # This method will do REST API call to RPS Engine API.
        __engine.transform_async_with_context_names(
            rps_values=[payment_date, payment_amount],
            rights_context_name="Admin",
            processing_context_name="Protect")

        print(f'{payment_date.instance.class_name}: {payment_date.instance.property_name}. \
            Original: {payment_date.original}. Transformed: {payment_date.transformed}')
        print(f'{payment_amount.instance.class_name}: {payment_amount.instance.property_name}. \
            Original: {payment_amount.original}. Transformed: {payment_amount.transformed}')
