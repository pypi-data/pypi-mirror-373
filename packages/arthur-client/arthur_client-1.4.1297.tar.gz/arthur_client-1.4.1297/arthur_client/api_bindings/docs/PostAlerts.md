# PostAlerts


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alerts** | [**List[PostAlert]**](PostAlert.md) | The list of alerts to create. | 

## Example

```python
from arthur_client.api_bindings.models.post_alerts import PostAlerts

# TODO update the JSON string below
json = "{}"
# create an instance of PostAlerts from a JSON string
post_alerts_instance = PostAlerts.from_json(json)
# print the JSON string representation of the object
print(PostAlerts.to_json())

# convert the object into a dict
post_alerts_dict = post_alerts_instance.to_dict()
# create an instance of PostAlerts from a dict
post_alerts_from_dict = PostAlerts.from_dict(post_alerts_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


