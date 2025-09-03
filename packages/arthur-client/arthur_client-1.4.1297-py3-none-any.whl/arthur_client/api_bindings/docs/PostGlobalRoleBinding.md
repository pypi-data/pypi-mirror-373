# PostGlobalRoleBinding


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_id** | **str** | ID of the bound role. | 
**bound_resource_kind** | [**BoundResourceKind**](BoundResourceKind.md) | Kind of the bound resource. | 
**resource_id** | **str** | Id of the bound resource. | 

## Example

```python
from arthur_client.api_bindings.models.post_global_role_binding import PostGlobalRoleBinding

# TODO update the JSON string below
json = "{}"
# create an instance of PostGlobalRoleBinding from a JSON string
post_global_role_binding_instance = PostGlobalRoleBinding.from_json(json)
# print the JSON string representation of the object
print(PostGlobalRoleBinding.to_json())

# convert the object into a dict
post_global_role_binding_dict = post_global_role_binding_instance.to_dict()
# create an instance of PostGlobalRoleBinding from a dict
post_global_role_binding_from_dict = PostGlobalRoleBinding.from_dict(post_global_role_binding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


