# CreateModelLinkTaskJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'link_model_task']
**task_id** | **str** | The id of the Shield task to link when creating the new model. | 
**connector_id** | **str** | The id of the engine internal connector to use to link the task. | 
**onboarding_identifier** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.create_model_link_task_job_spec import CreateModelLinkTaskJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of CreateModelLinkTaskJobSpec from a JSON string
create_model_link_task_job_spec_instance = CreateModelLinkTaskJobSpec.from_json(json)
# print the JSON string representation of the object
print(CreateModelLinkTaskJobSpec.to_json())

# convert the object into a dict
create_model_link_task_job_spec_dict = create_model_link_task_job_spec_instance.to_dict()
# create an instance of CreateModelLinkTaskJobSpec from a dict
create_model_link_task_job_spec_from_dict = CreateModelLinkTaskJobSpec.from_dict(create_model_link_task_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


