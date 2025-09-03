# ResourceListPermission


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Permission]**](Permission.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_permission import ResourceListPermission

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListPermission from a JSON string
resource_list_permission_instance = ResourceListPermission.from_json(json)
# print the JSON string representation of the object
print(ResourceListPermission.to_json())

# convert the object into a dict
resource_list_permission_dict = resource_list_permission_instance.to_dict()
# create an instance of ResourceListPermission from a dict
resource_list_permission_from_dict = ResourceListPermission.from_dict(resource_list_permission_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


