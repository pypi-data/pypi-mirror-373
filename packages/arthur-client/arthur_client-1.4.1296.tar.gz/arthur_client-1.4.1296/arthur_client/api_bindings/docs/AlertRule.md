# AlertRule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | The id of the alert rule. | 
**model_id** | **str** | The model id of the alert rule. | 
**name** | **str** | The name of the alert rule. | 
**description** | **str** |  | [optional] 
**threshold** | **float** | The threshold that will trigger the alert rule. | 
**bound** | [**AlertBound**](AlertBound.md) | The bound of the alert rule. | 
**query** | **str** | The query of the alert rule. | 
**metric_name** | **str** | The name of the metric returned by the alert rule query. | 
**interval** | [**AlertRuleInterval**](AlertRuleInterval.md) | The interval of the alert rule, commonly &#39;1 day&#39;, &#39;1 hour&#39;, etc. | 
**last_updated_by_user** | [**User**](User.md) |  | [optional] 
**notification_webhooks** | [**List[AlertRuleNotificationWebhook]**](AlertRuleNotificationWebhook.md) | Notification webhooks configured for the alert rule. | 

## Example

```python
from arthur_client.api_bindings.models.alert_rule import AlertRule

# TODO update the JSON string below
json = "{}"
# create an instance of AlertRule from a JSON string
alert_rule_instance = AlertRule.from_json(json)
# print the JSON string representation of the object
print(AlertRule.to_json())

# convert the object into a dict
alert_rule_dict = alert_rule_instance.to_dict()
# create an instance of AlertRule from a dict
alert_rule_from_dict = AlertRule.from_dict(alert_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


