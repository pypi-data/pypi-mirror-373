# User


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

## Example

```python
from arthur_client.api_bindings.models.user import User

# TODO update the JSON string below
json = "{}"
# create an instance of User from a JSON string
user_instance = User.from_json(json)
# print the JSON string representation of the object
print(User.to_json())

# convert the object into a dict
user_dict = user_instance.to_dict()
# create an instance of User from a dict
user_from_dict = User.from_dict(user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


