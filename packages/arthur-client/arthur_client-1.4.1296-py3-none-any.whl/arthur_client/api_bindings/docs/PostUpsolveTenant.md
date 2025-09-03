# PostUpsolveTenant


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_kind** | [**ResourceKind**](ResourceKind.md) | Kind of the resource the user wants a JWT to access data for in Upsolve. Supports model resource kind. | 
**resource_id** | **str** | ID of the resource. | 

## Example

```python
from arthur_client.api_bindings.models.post_upsolve_tenant import PostUpsolveTenant

# TODO update the JSON string below
json = "{}"
# create an instance of PostUpsolveTenant from a JSON string
post_upsolve_tenant_instance = PostUpsolveTenant.from_json(json)
# print the JSON string representation of the object
print(PostUpsolveTenant.to_json())

# convert the object into a dict
post_upsolve_tenant_dict = post_upsolve_tenant_instance.to_dict()
# create an instance of PostUpsolveTenant from a dict
post_upsolve_tenant_from_dict = PostUpsolveTenant.from_dict(post_upsolve_tenant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


