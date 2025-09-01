# PostTaskValidationAPIKey


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The Shield ID for the API key. | 
**name** | **str** | The user-friendly name of the API key. | 
**key** | **str** | The value of the API key. | 

## Example

```python
from arthur_client.api_bindings.models.post_task_validation_api_key import PostTaskValidationAPIKey

# TODO update the JSON string below
json = "{}"
# create an instance of PostTaskValidationAPIKey from a JSON string
post_task_validation_api_key_instance = PostTaskValidationAPIKey.from_json(json)
# print the JSON string representation of the object
print(PostTaskValidationAPIKey.to_json())

# convert the object into a dict
post_task_validation_api_key_dict = post_task_validation_api_key_instance.to_dict()
# create an instance of PostTaskValidationAPIKey from a dict
post_task_validation_api_key_from_dict = PostTaskValidationAPIKey.from_dict(post_task_validation_api_key_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


