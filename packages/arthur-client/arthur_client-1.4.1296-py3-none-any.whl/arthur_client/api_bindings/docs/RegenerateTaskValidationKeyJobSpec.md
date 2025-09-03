# RegenerateTaskValidationKeyJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'regenerate_validation_key']
**scope_model_id** | **str** | The ID of the model to regenerate the validation key for. | 

## Example

```python
from arthur_client.api_bindings.models.regenerate_task_validation_key_job_spec import RegenerateTaskValidationKeyJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of RegenerateTaskValidationKeyJobSpec from a JSON string
regenerate_task_validation_key_job_spec_instance = RegenerateTaskValidationKeyJobSpec.from_json(json)
# print the JSON string representation of the object
print(RegenerateTaskValidationKeyJobSpec.to_json())

# convert the object into a dict
regenerate_task_validation_key_job_spec_dict = regenerate_task_validation_key_job_spec_instance.to_dict()
# create an instance of RegenerateTaskValidationKeyJobSpec from a dict
regenerate_task_validation_key_job_spec_from_dict = RegenerateTaskValidationKeyJobSpec.from_dict(regenerate_task_validation_key_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


