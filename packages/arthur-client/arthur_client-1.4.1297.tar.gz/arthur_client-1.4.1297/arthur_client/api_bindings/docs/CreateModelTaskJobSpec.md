# CreateModelTaskJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'create_model_task']
**connector_id** | **str** | The id of the engine internal connector to use to create the task. | 
**task_name** | **str** | The name of the task. | 
**onboarding_identifier** | **str** |  | [optional] 
**initial_rules** | [**List[NewRuleRequest]**](NewRuleRequest.md) | The initial rules to apply to the created model. | 
**task_type** | [**TaskType**](TaskType.md) | The type of task to create. | [optional] 
**initial_metrics** | [**List[NewMetricRequest]**](NewMetricRequest.md) | The initial metrics to apply to agentic tasks. | 

## Example

```python
from arthur_client.api_bindings.models.create_model_task_job_spec import CreateModelTaskJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of CreateModelTaskJobSpec from a JSON string
create_model_task_job_spec_instance = CreateModelTaskJobSpec.from_json(json)
# print the JSON string representation of the object
print(CreateModelTaskJobSpec.to_json())

# convert the object into a dict
create_model_task_job_spec_dict = create_model_task_job_spec_instance.to_dict()
# create an instance of CreateModelTaskJobSpec from a dict
create_model_task_job_spec_from_dict = CreateModelTaskJobSpec.from_dict(create_model_task_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


