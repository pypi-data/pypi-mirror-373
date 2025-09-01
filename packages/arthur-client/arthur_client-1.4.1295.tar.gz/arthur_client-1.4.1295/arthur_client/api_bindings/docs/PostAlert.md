# PostAlert


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | 
**timestamp** | **datetime** | The timestamp of the alert. | 
**value** | **float** | The value of the metric that triggered the alert. | 
**threshold** | **float** | The threshold that triggered the alert. | 
**bound** | [**AlertBound**](AlertBound.md) | The bound of the alert. | 
**interval** | [**AlertRuleInterval**](AlertRuleInterval.md) | The interval of the alert rule, commonly &#39;1 day&#39;, &#39;1 hour&#39;, etc. | 
**dimensions** | **object** |  | 
**alert_rule_id** | **str** | The alert rule id of the alert. | 
**job_id** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_alert import PostAlert

# TODO update the JSON string below
json = "{}"
# create an instance of PostAlert from a JSON string
post_alert_instance = PostAlert.from_json(json)
# print the JSON string representation of the object
print(PostAlert.to_json())

# convert the object into a dict
post_alert_dict = post_alert_instance.to_dict()
# create an instance of PostAlert from a dict
post_alert_from_dict = PostAlert.from_dict(post_alert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


