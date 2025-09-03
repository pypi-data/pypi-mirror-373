# AlertRuleSQLValidationResp


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_metric_timestamp_col** | **bool** | The name of the metric returned by the alert rule query. | 
**has_metric_value_col** | **bool** | The name of the metric returned by the alert rule query. | 
**has_time_templates** | **bool** | The name of the metric returned by the alert rule query. | 
**has_interval_templates** | **bool** | The name of the metric returned by the alert rule query. | 

## Example

```python
from arthur_client.api_bindings.models.alert_rule_sql_validation_resp import AlertRuleSQLValidationResp

# TODO update the JSON string below
json = "{}"
# create an instance of AlertRuleSQLValidationResp from a JSON string
alert_rule_sql_validation_resp_instance = AlertRuleSQLValidationResp.from_json(json)
# print the JSON string representation of the object
print(AlertRuleSQLValidationResp.to_json())

# convert the object into a dict
alert_rule_sql_validation_resp_dict = alert_rule_sql_validation_resp_instance.to_dict()
# create an instance of AlertRuleSQLValidationResp from a dict
alert_rule_sql_validation_resp_from_dict = AlertRuleSQLValidationResp.from_dict(alert_rule_sql_validation_resp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


