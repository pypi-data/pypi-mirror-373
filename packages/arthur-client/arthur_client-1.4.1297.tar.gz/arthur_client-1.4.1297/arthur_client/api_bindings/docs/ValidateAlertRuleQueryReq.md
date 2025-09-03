# ValidateAlertRuleQueryReq


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **str** | The query of the alert rule. | 

## Example

```python
from arthur_client.api_bindings.models.validate_alert_rule_query_req import ValidateAlertRuleQueryReq

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateAlertRuleQueryReq from a JSON string
validate_alert_rule_query_req_instance = ValidateAlertRuleQueryReq.from_json(json)
# print the JSON string representation of the object
print(ValidateAlertRuleQueryReq.to_json())

# convert the object into a dict
validate_alert_rule_query_req_dict = validate_alert_rule_query_req_instance.to_dict()
# create an instance of ValidateAlertRuleQueryReq from a dict
validate_alert_rule_query_req_from_dict = ValidateAlertRuleQueryReq.from_dict(validate_alert_rule_query_req_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


