# ResourceListRoleBinding


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[RoleBinding]**](RoleBinding.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListRoleBinding from a JSON string
resource_list_role_binding_instance = ResourceListRoleBinding.from_json(json)
# print the JSON string representation of the object
print(ResourceListRoleBinding.to_json())

# convert the object into a dict
resource_list_role_binding_dict = resource_list_role_binding_instance.to_dict()
# create an instance of ResourceListRoleBinding from a dict
resource_list_role_binding_from_dict = ResourceListRoleBinding.from_dict(resource_list_role_binding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


