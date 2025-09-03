# PatchUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**picture** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_user import PatchUser

# TODO update the JSON string below
json = "{}"
# create an instance of PatchUser from a JSON string
patch_user_instance = PatchUser.from_json(json)
# print the JSON string representation of the object
print(PatchUser.to_json())

# convert the object into a dict
patch_user_dict = patch_user_instance.to_dict()
# create an instance of PatchUser from a dict
patch_user_from_dict = PatchUser.from_dict(patch_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


