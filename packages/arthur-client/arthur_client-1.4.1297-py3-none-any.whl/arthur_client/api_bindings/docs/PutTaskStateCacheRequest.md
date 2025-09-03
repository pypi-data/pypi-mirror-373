# PutTaskStateCacheRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task** | [**TaskResponse**](TaskResponse.md) | Copy of the task state to cache in the control plane. | 

## Example

```python
from arthur_client.api_bindings.models.put_task_state_cache_request import PutTaskStateCacheRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutTaskStateCacheRequest from a JSON string
put_task_state_cache_request_instance = PutTaskStateCacheRequest.from_json(json)
# print the JSON string representation of the object
print(PutTaskStateCacheRequest.to_json())

# convert the object into a dict
put_task_state_cache_request_dict = put_task_state_cache_request_instance.to_dict()
# create an instance of PutTaskStateCacheRequest from a dict
put_task_state_cache_request_from_dict = PutTaskStateCacheRequest.from_dict(put_task_state_cache_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


