# ConnectorCheckJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'connector_check']
**connector_id** | **str** | The id of the connector to check. | 

## Example

```python
from arthur_client.api_bindings.models.connector_check_job_spec import ConnectorCheckJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorCheckJobSpec from a JSON string
connector_check_job_spec_instance = ConnectorCheckJobSpec.from_json(json)
# print the JSON string representation of the object
print(ConnectorCheckJobSpec.to_json())

# convert the object into a dict
connector_check_job_spec_dict = connector_check_job_spec_instance.to_dict()
# create an instance of ConnectorCheckJobSpec from a dict
connector_check_job_spec_from_dict = ConnectorCheckJobSpec.from_dict(connector_check_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


