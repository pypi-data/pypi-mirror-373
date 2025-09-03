# JobDequeueParameters


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**memory_limit_mb** | **int** | Available memory in megabytes for job execution | 

## Example

```python
from arthur_client.api_bindings.models.job_dequeue_parameters import JobDequeueParameters

# TODO update the JSON string below
json = "{}"
# create an instance of JobDequeueParameters from a JSON string
job_dequeue_parameters_instance = JobDequeueParameters.from_json(json)
# print the JSON string representation of the object
print(JobDequeueParameters.to_json())

# convert the object into a dict
job_dequeue_parameters_dict = job_dequeue_parameters_instance.to_dict()
# create an instance of JobDequeueParameters from a dict
job_dequeue_parameters_from_dict = JobDequeueParameters.from_dict(job_dequeue_parameters_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


