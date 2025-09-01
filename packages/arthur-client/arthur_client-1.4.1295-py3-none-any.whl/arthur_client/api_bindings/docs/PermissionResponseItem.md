# PermissionResponseItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_kind** | [**ResourceKind**](ResourceKind.md) | Resource kind to check. | 
**resource_id** | **str** | Resource id to check permission for. | 
**permission_name** | [**PermissionName**](PermissionName.md) | Permission name to check on the given resource. | 
**allowed** | **bool** | Value indicating wheter the requested permission is allowed. | 

## Example

```python
from arthur_client.api_bindings.models.permission_response_item import PermissionResponseItem

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionResponseItem from a JSON string
permission_response_item_instance = PermissionResponseItem.from_json(json)
# print the JSON string representation of the object
print(PermissionResponseItem.to_json())

# convert the object into a dict
permission_response_item_dict = permission_response_item_instance.to_dict()
# create an instance of PermissionResponseItem from a dict
permission_response_item_from_dict = PermissionResponseItem.from_dict(permission_response_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


