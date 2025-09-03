# DeleteModelTaskJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'delete_model_task']
**scope_model_id** | **str** | The id of the model to delete. | 

## Example

```python
from arthur_client.api_bindings.models.delete_model_task_job_spec import DeleteModelTaskJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteModelTaskJobSpec from a JSON string
delete_model_task_job_spec_instance = DeleteModelTaskJobSpec.from_json(json)
# print the JSON string representation of the object
print(DeleteModelTaskJobSpec.to_json())

# convert the object into a dict
delete_model_task_job_spec_dict = delete_model_task_job_spec_instance.to_dict()
# create an instance of DeleteModelTaskJobSpec from a dict
delete_model_task_job_spec_from_dict = DeleteModelTaskJobSpec.from_dict(delete_model_task_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


