# AlertRuleInterval


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**unit** | [**IntervalUnit**](IntervalUnit.md) | Unit of time interval. Example: &#39;minutes&#39;. | 
**count** | **int** | Number of units in the interval. Example: &#39;5&#39;. | 

## Example

```python
from arthur_client.api_bindings.models.alert_rule_interval import AlertRuleInterval

# TODO update the JSON string below
json = "{}"
# create an instance of AlertRuleInterval from a JSON string
alert_rule_interval_instance = AlertRuleInterval.from_json(json)
# print the JSON string representation of the object
print(AlertRuleInterval.to_json())

# convert the object into a dict
alert_rule_interval_dict = alert_rule_interval_instance.to_dict()
# create an instance of AlertRuleInterval from a dict
alert_rule_interval_from_dict = AlertRuleInterval.from_dict(alert_rule_interval_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


