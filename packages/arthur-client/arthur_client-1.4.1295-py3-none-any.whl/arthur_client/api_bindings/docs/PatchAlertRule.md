# PatchAlertRule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**threshold** | **float** |  | [optional] 
**bound** | [**AlertBound**](AlertBound.md) |  | [optional] 
**query** | **str** |  | [optional] 
**metric_name** | **str** |  | [optional] 
**interval** | [**AlertRuleInterval**](AlertRuleInterval.md) |  | [optional] 
**notification_webhook_ids** | **List[str]** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_alert_rule import PatchAlertRule

# TODO update the JSON string below
json = "{}"
# create an instance of PatchAlertRule from a JSON string
patch_alert_rule_instance = PatchAlertRule.from_json(json)
# print the JSON string representation of the object
print(PatchAlertRule.to_json())

# convert the object into a dict
patch_alert_rule_dict = patch_alert_rule_instance.to_dict()
# create an instance of PatchAlertRule from a dict
patch_alert_rule_from_dict = PatchAlertRule.from_dict(patch_alert_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


