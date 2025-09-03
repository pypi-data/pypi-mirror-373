#  Quick Start Guide `rps-engine-client-python`

This guide explains how to install and use the `rps-engine-client-python` library from PyPI to interact with the REGDATA's RPS Engine API.



## Install the Library

Install the latest version from PyPI using pip:

```bash
pip install rps-engine-client-python
```


## Configure Your Environment

The library requires configuration for authentication and engine connection. 

The default location of the configuration file is the root project folder.

#### Using .Env file with Environment Variables

```python
rps__engineHostName="https://your-rps-engine-url"
rps__identityServiceHostName="https://your-identity-url"
rps__clientId="YOUR_CLIENT_ID"
rps__clientSecret="YOUR_CLIENT_SECRET"
rps__timeout=30

external_source_files__rightsContextsFilePath=path/to/rights_contexts.json
external_source_files__processingContextsFilePath=path/to/processing_contexts.json
```

#### rights_contexts.json
```JSON
{
  "Admin": {
    "evidences": [
      {
        "name": "Role",
        "value": "Admin"
      }
    ]
  }
}
```
#### processing_contexts.json

```JSON
{
  "Protect": {
    "evidences": [
      {
        "name": "Action",
        "value": "Protect"
      }
    ]
  },
  "Deprotect": {
    "evidences": [
      {
        "name": "Action",
        "value": "Deprotect"
      }
    ]
  }
}
```

## Create a Python Script


Below is an example which uses the [`EngineFactory`](Client/engine/engine_factory.py) class for the engine connection, getting the contexts from a JSON file.

- Pay attention that the given arguments for the `rights_context_name` and `processing_context_name` parameters are the names of keys from the *rights_contexts.json* and *processing_contexts.json* files above.
```python
from Client.engine.engine_factory import EngineFactory
from Client.context_source import ContextSource
from Client.instance.rps_instance import RPSInstance
from Client.engine_context.processing_context import ProcessingContext
from Client.engine_context.rights_context import RightsContext
from Client.evidence import Evidence
from Client.value.rps_value import RPSValue

engine = EngineFactory.get_engine(context_source=ContextSource.JSON)

raw_first_name = RPSValue(instance=RPSInstance(className='User', propertyName='Name'), originalValue='Jonny')

request_context = engine.create_context().with_request_by_context_names(
    rps_values=[raw_first_name],
    rights_context_name='Admin',
    processing_context_name='Protect')

request_context.transform_async()

print(f'Original: {raw_first_name.original}, Transformed: {raw_first_name.transformed}')
```


## Run Your Script


```bash
python your_script.py
```


## Additional Resources

For advanced usage, examples, and contribution guidelines, see the [full documentation on GitHub](https://github.com/RegdataSA/rps-engine-client-python/).

For REGDATA Community Page see [RPS Community](https://demo.rpsprod.ch/community/).
