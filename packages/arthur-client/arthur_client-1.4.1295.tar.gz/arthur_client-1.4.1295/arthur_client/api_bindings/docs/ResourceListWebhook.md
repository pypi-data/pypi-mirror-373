# ResourceListWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Webhook]**](Webhook.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_webhook import ResourceListWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListWebhook from a JSON string
resource_list_webhook_instance = ResourceListWebhook.from_json(json)
# print the JSON string representation of the object
print(ResourceListWebhook.to_json())

# convert the object into a dict
resource_list_webhook_dict = resource_list_webhook_instance.to_dict()
# create an instance of ResourceListWebhook from a dict
resource_list_webhook_from_dict = ResourceListWebhook.from_dict(resource_list_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


