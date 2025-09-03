# PostEndUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** | The user&#39;s first name. | 
**last_name** | **str** |  | [optional] 
**email** | **str** | The user&#39;s email. | 
**password** | **str** | One time password for the user. | 
**picture** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_end_user import PostEndUser

# TODO update the JSON string below
json = "{}"
# create an instance of PostEndUser from a JSON string
post_end_user_instance = PostEndUser.from_json(json)
# print the JSON string representation of the object
print(PostEndUser.to_json())

# convert the object into a dict
post_end_user_dict = post_end_user_instance.to_dict()
# create an instance of PostEndUser from a dict
post_end_user_from_dict = PostEndUser.from_dict(post_end_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


