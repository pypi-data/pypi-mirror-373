# SensitiveUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**organization_id** | **str** | The ID of the Arthur organization the user belongs to. | 
**id** | **str** | Unique user ID assigned by Arthur. | 
**first_name** | **str** | The user&#39;s first name. | 
**last_name** | **str** |  | 
**email** | **str** |  | [optional] 
**picture** | **str** |  | [optional] 
**user_type** | [**UserType**](UserType.md) | The type of user. | 
**data_plane_id** | **str** |  | [optional] 
**client_id** | **str** |  | [optional] 
**organization_name** | **str** | Name of user&#39;s Arthur organization. | 
**credentials** | [**Credentials**](Credentials.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.sensitive_user import SensitiveUser

# TODO update the JSON string below
json = "{}"
# create an instance of SensitiveUser from a JSON string
sensitive_user_instance = SensitiveUser.from_json(json)
# print the JSON string representation of the object
print(SensitiveUser.to_json())

# convert the object into a dict
sensitive_user_dict = sensitive_user_instance.to_dict()
# create an instance of SensitiveUser from a dict
sensitive_user_from_dict = SensitiveUser.from_dict(sensitive_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


