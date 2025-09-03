# FetchModelTaskJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'fetch_model_task']
**scope_model_id** | **str** | The id of the model to fetch its corresponding task. | 

## Example

```python
from arthur_client.api_bindings.models.fetch_model_task_job_spec import FetchModelTaskJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of FetchModelTaskJobSpec from a JSON string
fetch_model_task_job_spec_instance = FetchModelTaskJobSpec.from_json(json)
# print the JSON string representation of the object
print(FetchModelTaskJobSpec.to_json())

# convert the object into a dict
fetch_model_task_job_spec_dict = fetch_model_task_job_spec_instance.to_dict()
# create an instance of FetchModelTaskJobSpec from a dict
fetch_model_task_job_spec_from_dict = FetchModelTaskJobSpec.from_dict(fetch_model_task_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


