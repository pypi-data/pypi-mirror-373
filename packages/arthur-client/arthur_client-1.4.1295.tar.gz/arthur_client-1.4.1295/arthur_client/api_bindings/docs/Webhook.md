# Webhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of webhook. | 
**url** | **str** | URL of the webhook. | 
**headers** | **Dict[str, List[str]]** | List of headers for the webhook. | [optional] 
**body** | **str** | Body of the webhook. | 
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | The id of the webhook. | 
**workspace_id** | **str** | ID of the parent workspace. | 
**last_updated_by_user** | [**User**](User.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.webhook import Webhook

# TODO update the JSON string below
json = "{}"
# create an instance of Webhook from a JSON string
webhook_instance = Webhook.from_json(json)
# print the JSON string representation of the object
print(Webhook.to_json())

# convert the object into a dict
webhook_dict = webhook_instance.to_dict()
# create an instance of Webhook from a dict
webhook_from_dict = Webhook.from_dict(webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


