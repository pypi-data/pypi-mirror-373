# ConnectorSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | Connector id. | 
**connector_type** | [**ConnectorType**](ConnectorType.md) | Type of connector. | 
**name** | **str** | Name of connector. | 
**temporary** | **bool** | True if connector is temporary (ie for testing only), false otherwise. | 
**fields** | [**List[ConnectorSpecFieldWithMetadata]**](ConnectorSpecFieldWithMetadata.md) | List of fields for the connector. | 
**last_updated_by_user** | [**User**](User.md) |  | [optional] 
**connector_check_result** | [**ConnectorCheckResult**](ConnectorCheckResult.md) |  | [optional] 
**project_id** | **str** | ID of parent project. | 
**data_plane_id** | **str** | ID of the data plane that will execute the connection. Should be formatted as a UUID. | 

## Example

```python
from arthur_client.api_bindings.models.connector_spec import ConnectorSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorSpec from a JSON string
connector_spec_instance = ConnectorSpec.from_json(json)
# print the JSON string representation of the object
print(ConnectorSpec.to_json())

# convert the object into a dict
connector_spec_dict = connector_spec_instance.to_dict()
# create an instance of ConnectorSpec from a dict
connector_spec_from_dict = ConnectorSpec.from_dict(connector_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


