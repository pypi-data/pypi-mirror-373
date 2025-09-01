# TaskReadResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task** | [**TaskResponse**](TaskResponse.md) |  | [optional] 
**last_synced_at** | **datetime** |  | [optional] 
**scope_model_id** | **str** | The ID of the corresponding scope model for this task. | 

## Example

```python
from arthur_client.api_bindings.models.task_read_response import TaskReadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TaskReadResponse from a JSON string
task_read_response_instance = TaskReadResponse.from_json(json)
# print the JSON string representation of the object
print(TaskReadResponse.to_json())

# convert the object into a dict
task_read_response_dict = task_read_response_instance.to_dict()
# create an instance of TaskReadResponse from a dict
task_read_response_from_dict = TaskReadResponse.from_dict(task_read_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


