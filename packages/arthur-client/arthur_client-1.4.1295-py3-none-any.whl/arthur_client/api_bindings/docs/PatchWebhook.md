# PatchWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**url** | **str** |  | [optional] 
**headers** | **Dict[str, List[str]]** |  | [optional] 
**body** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_webhook import PatchWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of PatchWebhook from a JSON string
patch_webhook_instance = PatchWebhook.from_json(json)
# print the JSON string representation of the object
print(PatchWebhook.to_json())

# convert the object into a dict
patch_webhook_dict = patch_webhook_instance.to_dict()
# create an instance of PatchWebhook from a dict
patch_webhook_from_dict = PatchWebhook.from_dict(patch_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


