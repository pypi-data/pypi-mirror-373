# PostRoleBinding


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_id** | **str** | ID of the bound role. | 
**user_id** | **str** |  | [optional] 
**group_id** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_role_binding import PostRoleBinding

# TODO update the JSON string below
json = "{}"
# create an instance of PostRoleBinding from a JSON string
post_role_binding_instance = PostRoleBinding.from_json(json)
# print the JSON string representation of the object
print(PostRoleBinding.to_json())

# convert the object into a dict
post_role_binding_dict = post_role_binding_instance.to_dict()
# create an instance of PostRoleBinding from a dict
post_role_binding_from_dict = PostRoleBinding.from_dict(post_role_binding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


