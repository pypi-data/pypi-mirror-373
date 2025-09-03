# ResourceListConnectorSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[ConnectorSpec]**](ConnectorSpec.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_connector_spec import ResourceListConnectorSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListConnectorSpec from a JSON string
resource_list_connector_spec_instance = ResourceListConnectorSpec.from_json(json)
# print the JSON string representation of the object
print(ResourceListConnectorSpec.to_json())

# convert the object into a dict
resource_list_connector_spec_dict = resource_list_connector_spec_instance.to_dict()
# create an instance of ResourceListConnectorSpec from a dict
resource_list_connector_spec_from_dict = ResourceListConnectorSpec.from_dict(resource_list_connector_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


