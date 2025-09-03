# JobRun


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID for the job run. | 
**job_id** | **str** | The parent job for this job run. | 
**state** | [**JobState**](JobState.md) | Current state of the job run. | 
**job_attempt** | **int** | The attempt number of the job. | 
**start_timestamp** | **datetime** | The timestamp this job run was started. | 
**end_timestamp** | **datetime** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.job_run import JobRun

# TODO update the JSON string below
json = "{}"
# create an instance of JobRun from a JSON string
job_run_instance = JobRun.from_json(json)
# print the JSON string representation of the object
print(JobRun.to_json())

# convert the object into a dict
job_run_dict = job_run_instance.to_dict()
# create an instance of JobRun from a dict
job_run_from_dict = JobRun.from_dict(job_run_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


