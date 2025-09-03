# UserServiceAccountCredentials


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
**credentials** | [**ServiceAccountCredentials**](ServiceAccountCredentials.md) | The service account credentials. | 

## Example

```python
from arthur_client.api_bindings.models.user_service_account_credentials import UserServiceAccountCredentials

# TODO update the JSON string below
json = "{}"
# create an instance of UserServiceAccountCredentials from a JSON string
user_service_account_credentials_instance = UserServiceAccountCredentials.from_json(json)
# print the JSON string representation of the object
print(UserServiceAccountCredentials.to_json())

# convert the object into a dict
user_service_account_credentials_dict = user_service_account_credentials_instance.to_dict()
# create an instance of UserServiceAccountCredentials from a dict
user_service_account_credentials_from_dict = UserServiceAccountCredentials.from_dict(user_service_account_credentials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


