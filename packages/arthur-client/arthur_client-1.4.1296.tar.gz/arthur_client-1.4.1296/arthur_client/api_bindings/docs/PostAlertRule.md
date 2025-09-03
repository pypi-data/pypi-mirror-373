# PostAlertRule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the alert rule. | 
**description** | **str** |  | [optional] 
**threshold** | **float** | The threshold that will trigger the alert rule. | 
**bound** | [**AlertBound**](AlertBound.md) | The bound of the alert rule. | 
**query** | **str** | The query of the alert rule. | 
**metric_name** | **str** | The name of the metric returned by the alert rule query. | 
**interval** | [**AlertRuleInterval**](AlertRuleInterval.md) | The interval of the alert rule, commonly &#39;1 day&#39;, &#39;1 hour&#39;, etc. | 
**notification_webhook_ids** | **List[str]** | The notification webhook IDs where the alert rule will send alert notification. | [optional] [default to []]

## Example

```python
from arthur_client.api_bindings.models.post_alert_rule import PostAlertRule

# TODO update the JSON string below
json = "{}"
# create an instance of PostAlertRule from a JSON string
post_alert_rule_instance = PostAlertRule.from_json(json)
# print the JSON string representation of the object
print(PostAlertRule.to_json())

# convert the object into a dict
post_alert_rule_dict = post_alert_rule_instance.to_dict()
# create an instance of PostAlertRule from a dict
post_alert_rule_from_dict = PostAlertRule.from_dict(post_alert_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


