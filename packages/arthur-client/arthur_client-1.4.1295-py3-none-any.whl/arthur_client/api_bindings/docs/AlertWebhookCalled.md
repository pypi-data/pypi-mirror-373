# AlertWebhookCalled


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webhook_id** | **str** | The id of the webhook that was triggered by the alert. | 
**webhook_name** | **str** | The name of the webhook. | 
**webhook_result** | [**WebhookResult**](WebhookResult.md) | The result of the webhook call. | 

## Example

```python
from arthur_client.api_bindings.models.alert_webhook_called import AlertWebhookCalled

# TODO update the JSON string below
json = "{}"
# create an instance of AlertWebhookCalled from a JSON string
alert_webhook_called_instance = AlertWebhookCalled.from_json(json)
# print the JSON string representation of the object
print(AlertWebhookCalled.to_json())

# convert the object into a dict
alert_webhook_called_dict = alert_webhook_called_instance.to_dict()
# create an instance of AlertWebhookCalled from a dict
alert_webhook_called_from_dict = AlertWebhookCalled.from_dict(alert_webhook_called_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


