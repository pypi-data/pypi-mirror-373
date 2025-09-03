# TaskConnectionInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**validation_key** | [**TaskValidationAPIKey**](TaskValidationAPIKey.md) | The information for the API key with validation permissions for the task. | 
**api_host** | **str** | Host for the task. | 

## Example

```python
from arthur_client.api_bindings.models.task_connection_info import TaskConnectionInfo

# TODO update the JSON string below
json = "{}"
# create an instance of TaskConnectionInfo from a JSON string
task_connection_info_instance = TaskConnectionInfo.from_json(json)
# print the JSON string representation of the object
print(TaskConnectionInfo.to_json())

# convert the object into a dict
task_connection_info_dict = task_connection_info_instance.to_dict()
# create an instance of TaskConnectionInfo from a dict
task_connection_info_from_dict = TaskConnectionInfo.from_dict(task_connection_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


