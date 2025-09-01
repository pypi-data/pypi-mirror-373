# ResourceListRole


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Role]**](Role.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_role import ResourceListRole

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListRole from a JSON string
resource_list_role_instance = ResourceListRole.from_json(json)
# print the JSON string representation of the object
print(ResourceListRole.to_json())

# convert the object into a dict
resource_list_role_dict = resource_list_role_instance.to_dict()
# create an instance of ResourceListRole from a dict
resource_list_role_from_dict = ResourceListRole.from_dict(resource_list_role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


