# ResourceListAlertRule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[AlertRule]**](AlertRule.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_alert_rule import ResourceListAlertRule

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListAlertRule from a JSON string
resource_list_alert_rule_instance = ResourceListAlertRule.from_json(json)
# print the JSON string representation of the object
print(ResourceListAlertRule.to_json())

# convert the object into a dict
resource_list_alert_rule_dict = resource_list_alert_rule_instance.to_dict()
# create an instance of ResourceListAlertRule from a dict
resource_list_alert_rule_from_dict = ResourceListAlertRule.from_dict(resource_list_alert_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


