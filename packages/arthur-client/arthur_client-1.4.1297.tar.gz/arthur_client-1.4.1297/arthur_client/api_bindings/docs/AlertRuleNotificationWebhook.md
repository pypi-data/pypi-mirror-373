# AlertRuleNotificationWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Webhook ID. | 
**name** | **str** | Webhook name. | 

## Example

```python
from arthur_client.api_bindings.models.alert_rule_notification_webhook import AlertRuleNotificationWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of AlertRuleNotificationWebhook from a JSON string
alert_rule_notification_webhook_instance = AlertRuleNotificationWebhook.from_json(json)
# print the JSON string representation of the object
print(AlertRuleNotificationWebhook.to_json())

# convert the object into a dict
alert_rule_notification_webhook_dict = alert_rule_notification_webhook_instance.to_dict()
# create an instance of AlertRuleNotificationWebhook from a dict
alert_rule_notification_webhook_from_dict = AlertRuleNotificationWebhook.from_dict(alert_rule_notification_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


