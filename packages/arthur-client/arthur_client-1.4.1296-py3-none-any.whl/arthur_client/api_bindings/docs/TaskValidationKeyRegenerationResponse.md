# TaskValidationKeyRegenerationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | Job ID executing the validation key regeneration. | 

## Example

```python
from arthur_client.api_bindings.models.task_validation_key_regeneration_response import TaskValidationKeyRegenerationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TaskValidationKeyRegenerationResponse from a JSON string
task_validation_key_regeneration_response_instance = TaskValidationKeyRegenerationResponse.from_json(json)
# print the JSON string representation of the object
print(TaskValidationKeyRegenerationResponse.to_json())

# convert the object into a dict
task_validation_key_regeneration_response_dict = task_validation_key_regeneration_response_instance.to_dict()
# create an instance of TaskValidationKeyRegenerationResponse from a dict
task_validation_key_regeneration_response_from_dict = TaskValidationKeyRegenerationResponse.from_dict(task_validation_key_regeneration_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


