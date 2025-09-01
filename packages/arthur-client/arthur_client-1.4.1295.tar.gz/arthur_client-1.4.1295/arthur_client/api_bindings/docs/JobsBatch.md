# JobsBatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jobs** | [**List[Job]**](Job.md) | List of jobs. | 

## Example

```python
from arthur_client.api_bindings.models.jobs_batch import JobsBatch

# TODO update the JSON string below
json = "{}"
# create an instance of JobsBatch from a JSON string
jobs_batch_instance = JobsBatch.from_json(json)
# print the JSON string representation of the object
print(JobsBatch.to_json())

# convert the object into a dict
jobs_batch_dict = jobs_batch_instance.to_dict()
# create an instance of JobsBatch from a dict
jobs_batch_from_dict = JobsBatch.from_dict(jobs_batch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


