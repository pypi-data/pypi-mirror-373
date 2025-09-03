# UpdateModelTaskRulesJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'update_model_task_rules']
**scope_model_id** | **str** | The id of the model to update the task rules. | 
**rules_to_enable** | **List[str]** | The list of rule IDs to enable on the task. | [optional] 
**rules_to_disable** | **List[str]** | The list of rule IDs to disable on the task. | [optional] 
**rules_to_archive** | **List[str]** | The list of rule IDs to archive on the task. | [optional] 
**rules_to_add** | [**List[NewRuleRequest]**](NewRuleRequest.md) | The new rules to add to the task. | [optional] 

## Example

```python
from arthur_client.api_bindings.models.update_model_task_rules_job_spec import UpdateModelTaskRulesJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateModelTaskRulesJobSpec from a JSON string
update_model_task_rules_job_spec_instance = UpdateModelTaskRulesJobSpec.from_json(json)
# print the JSON string representation of the object
print(UpdateModelTaskRulesJobSpec.to_json())

# convert the object into a dict
update_model_task_rules_job_spec_dict = update_model_task_rules_job_spec_instance.to_dict()
# create an instance of UpdateModelTaskRulesJobSpec from a dict
update_model_task_rules_job_spec_from_dict = UpdateModelTaskRulesJobSpec.from_dict(update_model_task_rules_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


