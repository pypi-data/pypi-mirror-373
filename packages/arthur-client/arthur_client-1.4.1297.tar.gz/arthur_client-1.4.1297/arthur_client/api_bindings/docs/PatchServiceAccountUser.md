# PatchServiceAccountUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_service_account_user import PatchServiceAccountUser

# TODO update the JSON string below
json = "{}"
# create an instance of PatchServiceAccountUser from a JSON string
patch_service_account_user_instance = PatchServiceAccountUser.from_json(json)
# print the JSON string representation of the object
print(PatchServiceAccountUser.to_json())

# convert the object into a dict
patch_service_account_user_dict = patch_service_account_user_instance.to_dict()
# create an instance of PatchServiceAccountUser from a dict
patch_service_account_user_from_dict = PatchServiceAccountUser.from_dict(patch_service_account_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


