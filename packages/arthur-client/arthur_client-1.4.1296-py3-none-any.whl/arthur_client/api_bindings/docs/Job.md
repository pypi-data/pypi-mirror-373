# Job


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | UUID of the job. | 
**kind** | [**JobKind**](JobKind.md) | Type of job. | 
**job_spec** | [**JobSpec**](JobSpec.md) |  | 
**state** | [**JobState**](JobState.md) | Current state of the job. | 
**project_id** | **str** | ID of parent project. | 
**data_plane_id** | **str** |  | [optional] 
**queued_at** | **datetime** | ISO 8601 timestamp when the job was queued. | 
**ready_at** | **datetime** | ISO 8601 timestamp of the earliest time the job can be executed. | 
**started_at** | **datetime** |  | [optional] 
**finished_at** | **datetime** |  | [optional] 
**duration_sec** | **int** |  | [optional] 
**error_count** | **int** |  | [optional] 
**trigger_type** | [**JobTrigger**](JobTrigger.md) | Type of trigger. | 
**triggered_by_user** | [**User**](User.md) |  | [optional] 
**schedule_id** | **str** |  | [optional] 
**attempts** | **int** | Number of times the job was attempted. | 
**max_attempts** | **int** | Max number of times the job can fail and be retried. | 
**nonce** | **str** |  | [optional] 
**memory_requirements_mb** | **int** | Memory requirements for the job in megabytes. | 
**job_priority** | [**JobPriority**](JobPriority.md) | Priority of the job. | 

## Example

```python
from arthur_client.api_bindings.models.job import Job

# TODO update the JSON string below
json = "{}"
# create an instance of Job from a JSON string
job_instance = Job.from_json(json)
# print the JSON string representation of the object
print(Job.to_json())

# convert the object into a dict
job_dict = job_instance.to_dict()
# create an instance of Job from a dict
job_from_dict = Job.from_dict(job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


