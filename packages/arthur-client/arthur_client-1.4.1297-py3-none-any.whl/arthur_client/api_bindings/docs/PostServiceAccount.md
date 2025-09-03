# PostServiceAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The service account&#39;s name. | 

## Example

```python
from arthur_client.api_bindings.models.post_service_account import PostServiceAccount

# TODO update the JSON string below
json = "{}"
# create an instance of PostServiceAccount from a JSON string
post_service_account_instance = PostServiceAccount.from_json(json)
# print the JSON string representation of the object
print(PostServiceAccount.to_json())

# convert the object into a dict
post_service_account_dict = post_service_account_instance.to_dict()
# create an instance of PostServiceAccount from a dict
post_service_account_from_dict = PostServiceAccount.from_dict(post_service_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


