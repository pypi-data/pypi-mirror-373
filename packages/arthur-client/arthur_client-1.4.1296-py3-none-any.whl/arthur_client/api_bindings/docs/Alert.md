# Alert


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
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | The id of the alert. | 
**model_id** | **str** | The model id of the alert. | 
**alert_rule_name** | **str** | The name of the alert rule. | 
**alert_rule_metric_name** | **str** | The name of the metric returned by the alert rule query. | 
**is_duplicate_of** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.alert import Alert

# TODO update the JSON string below
json = "{}"
# create an instance of Alert from a JSON string
alert_instance = Alert.from_json(json)
# print the JSON string representation of the object
print(Alert.to_json())

# convert the object into a dict
alert_dict = alert_instance.to_dict()
# create an instance of Alert from a dict
alert_from_dict = Alert.from_dict(alert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


