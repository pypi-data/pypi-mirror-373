# TaskMutationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | Job ID executing the task mutation and retrieval. | 

## Example

```python
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TaskMutationResponse from a JSON string
task_mutation_response_instance = TaskMutationResponse.from_json(json)
# print the JSON string representation of the object
print(TaskMutationResponse.to_json())

# convert the object into a dict
task_mutation_response_dict = task_mutation_response_instance.to_dict()
# create an instance of TaskMutationResponse from a dict
task_mutation_response_from_dict = TaskMutationResponse.from_dict(task_mutation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


