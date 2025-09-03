# PatchTaskRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rules_to_enable** | **List[str]** | List of rule IDs to enable on the task. | [optional] 
**rules_to_disable** | **List[str]** | List of rule IDs to disable on the task. | [optional] 
**rules_to_archive** | **List[str]** | List of rule IDs to archive on the task. | [optional] 
**rules_to_add** | [**List[NewRuleRequest]**](NewRuleRequest.md) | List of new rules to add to the task. | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_task_request import PatchTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchTaskRequest from a JSON string
patch_task_request_instance = PatchTaskRequest.from_json(json)
# print the JSON string representation of the object
print(PatchTaskRequest.to_json())

# convert the object into a dict
patch_task_request_dict = patch_task_request_instance.to_dict()
# create an instance of PatchTaskRequest from a dict
patch_task_request_from_dict = PatchTaskRequest.from_dict(patch_task_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


