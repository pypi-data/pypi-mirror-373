# InviteNewUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | The user&#39;s email. | 
**role_binding** | [**PostGlobalRoleBinding**](PostGlobalRoleBinding.md) |  | [optional] 
**group_ids** | **List[str]** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.invite_new_user import InviteNewUser

# TODO update the JSON string below
json = "{}"
# create an instance of InviteNewUser from a JSON string
invite_new_user_instance = InviteNewUser.from_json(json)
# print the JSON string representation of the object
print(InviteNewUser.to_json())

# convert the object into a dict
invite_new_user_dict = invite_new_user_instance.to_dict()
# create an instance of InviteNewUser from a dict
invite_new_user_from_dict = InviteNewUser.from_dict(invite_new_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


