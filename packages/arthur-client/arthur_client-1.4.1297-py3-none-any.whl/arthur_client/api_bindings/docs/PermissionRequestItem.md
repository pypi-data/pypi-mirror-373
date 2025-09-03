# PermissionRequestItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_kind** | [**ResourceKind**](ResourceKind.md) | Resource kind to check. | 
**resource_id** | **str** | Resource id to check permission for. | 
**permission_name** | [**PermissionName**](PermissionName.md) | Permission name to check on the given resource. | 

## Example

```python
from arthur_client.api_bindings.models.permission_request_item import PermissionRequestItem

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionRequestItem from a JSON string
permission_request_item_instance = PermissionRequestItem.from_json(json)
# print the JSON string representation of the object
print(PermissionRequestItem.to_json())

# convert the object into a dict
permission_request_item_dict = permission_request_item_instance.to_dict()
# create an instance of PermissionRequestItem from a dict
permission_request_item_from_dict = PermissionRequestItem.from_dict(permission_request_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


