# PostWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of webhook. | 
**url** | **str** | URL of the webhook. | 
**headers** | **Dict[str, List[str]]** | List of headers for the webhook. | [optional] 
**body** | **str** | Body of the webhook. | 

## Example

```python
from arthur_client.api_bindings.models.post_webhook import PostWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of PostWebhook from a JSON string
post_webhook_instance = PostWebhook.from_json(json)
# print the JSON string representation of the object
print(PostWebhook.to_json())

# convert the object into a dict
post_webhook_dict = post_webhook_instance.to_dict()
# create an instance of PostWebhook from a dict
post_webhook_from_dict = PostWebhook.from_dict(post_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


