# RegisterUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | The user&#39;s email. | 

## Example

```python
from arthur_client.api_bindings.models.register_user import RegisterUser

# TODO update the JSON string below
json = "{}"
# create an instance of RegisterUser from a JSON string
register_user_instance = RegisterUser.from_json(json)
# print the JSON string representation of the object
print(RegisterUser.to_json())

# convert the object into a dict
register_user_dict = register_user_instance.to_dict()
# create an instance of RegisterUser from a dict
register_user_from_dict = RegisterUser.from_dict(register_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


