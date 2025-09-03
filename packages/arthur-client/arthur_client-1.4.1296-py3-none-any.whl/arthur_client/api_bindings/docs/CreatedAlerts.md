# CreatedAlerts


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alerts** | [**List[Alert]**](Alert.md) | The list of created alerts. | 
**webhooks_called** | [**List[AlertWebhookCalled]**](AlertWebhookCalled.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.created_alerts import CreatedAlerts

# TODO update the JSON string below
json = "{}"
# create an instance of CreatedAlerts from a JSON string
created_alerts_instance = CreatedAlerts.from_json(json)
# print the JSON string representation of the object
print(CreatedAlerts.to_json())

# convert the object into a dict
created_alerts_dict = created_alerts_instance.to_dict()
# create an instance of CreatedAlerts from a dict
created_alerts_from_dict = CreatedAlerts.from_dict(created_alerts_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


