# PatchJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_attempts** | **int** |  | 

## Example

```python
from arthur_client.api_bindings.models.patch_job import PatchJob

# TODO update the JSON string below
json = "{}"
# create an instance of PatchJob from a JSON string
patch_job_instance = PatchJob.from_json(json)
# print the JSON string representation of the object
print(PatchJob.to_json())

# convert the object into a dict
patch_job_dict = patch_job_instance.to_dict()
# create an instance of PatchJob from a dict
patch_job_from_dict = PatchJob.from_dict(patch_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


