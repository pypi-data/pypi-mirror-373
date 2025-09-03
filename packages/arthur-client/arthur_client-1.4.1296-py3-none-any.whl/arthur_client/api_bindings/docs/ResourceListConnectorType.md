# ResourceListConnectorType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[ConnectorType]**](ConnectorType.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_connector_type import ResourceListConnectorType

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListConnectorType from a JSON string
resource_list_connector_type_instance = ResourceListConnectorType.from_json(json)
# print the JSON string representation of the object
print(ResourceListConnectorType.to_json())

# convert the object into a dict
resource_list_connector_type_dict = resource_list_connector_type_instance.to_dict()
# create an instance of ResourceListConnectorType from a dict
resource_list_connector_type_from_dict = ResourceListConnectorType.from_dict(resource_list_connector_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


