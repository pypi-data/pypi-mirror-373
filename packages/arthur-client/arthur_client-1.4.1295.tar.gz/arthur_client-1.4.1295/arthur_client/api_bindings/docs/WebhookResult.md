# WebhookResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** |  | 
**response** | [**WebhookResponse**](WebhookResponse.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.webhook_result import WebhookResult

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookResult from a JSON string
webhook_result_instance = WebhookResult.from_json(json)
# print the JSON string representation of the object
print(WebhookResult.to_json())

# convert the object into a dict
webhook_result_dict = webhook_result_instance.to_dict()
# create an instance of WebhookResult from a dict
webhook_result_from_dict = WebhookResult.from_dict(webhook_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


