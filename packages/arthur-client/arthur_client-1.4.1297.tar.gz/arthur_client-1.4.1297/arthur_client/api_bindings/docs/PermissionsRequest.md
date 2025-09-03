# PermissionsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**permissions** | [**List[PermissionRequestItem]**](PermissionRequestItem.md) | List of checked permissions with their respective values. At least 1 permissions needs to be provided and 100 at most. | 

## Example

```python
from arthur_client.api_bindings.models.permissions_request import PermissionsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PermissionsRequest from a JSON string
permissions_request_instance = PermissionsRequest.from_json(json)
# print the JSON string representation of the object
print(PermissionsRequest.to_json())

# convert the object into a dict
permissions_request_dict = permissions_request_instance.to_dict()
# create an instance of PermissionsRequest from a dict
permissions_request_from_dict = PermissionsRequest.from_dict(permissions_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


