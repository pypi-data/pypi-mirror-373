# ScheduleJobsJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'schedule_jobs']
**scope_model_id** | **str** | The ID of the model to source the schedule from. | 
**start_timestamp** | **datetime** | Inclusive timestamp marking the start of the job series. | 

## Example

```python
from arthur_client.api_bindings.models.schedule_jobs_job_spec import ScheduleJobsJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ScheduleJobsJobSpec from a JSON string
schedule_jobs_job_spec_instance = ScheduleJobsJobSpec.from_json(json)
# print the JSON string representation of the object
print(ScheduleJobsJobSpec.to_json())

# convert the object into a dict
schedule_jobs_job_spec_dict = schedule_jobs_job_spec_instance.to_dict()
# create an instance of ScheduleJobsJobSpec from a dict
schedule_jobs_job_spec_from_dict = ScheduleJobsJobSpec.from_dict(schedule_jobs_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


