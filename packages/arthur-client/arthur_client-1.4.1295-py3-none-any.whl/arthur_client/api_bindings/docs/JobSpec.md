# JobSpec

Job specification for the job kind.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'link_model_task']
**dataset_id** | **str** |  | [optional] 
**available_dataset_id** | **str** | The id of the dataset within the connector to inspect the schema. | 
**start_timestamp** | **datetime** | Inclusive timestamp marking the start of the job series. | 
**end_timestamp** | **datetime** | The end timestamp to use for fetching data. | 
**operation_id** | **str** | The id of the data retrieval operation. | 
**data_filters** | [**List[DataResultFilter]**](DataResultFilter.md) | Filters to apply to the metrics data. | 
**pagination_options** | [**ConnectorPaginationOptions**](ConnectorPaginationOptions.md) | Pagination options to use for fetching data. | 
**scope_model_id** | **str** | The ID of the model to regenerate the validation key for. | 
**connector_id** | **str** | The id of the engine internal connector to use to link the task. | 
**check_range_start_timestamp** | **datetime** | The start timestamp to use for checking the alerts on the data. | 
**check_range_end_timestamp** | **datetime** | The end timestamp to use for checking the alerts on the data. | 
**task_name** | **str** | The name of the task. | 
**onboarding_identifier** | **str** |  | [optional] 
**initial_rules** | [**List[NewRuleRequest]**](NewRuleRequest.md) | The initial rules to apply to the created model. | 
**task_type** | [**TaskType**](TaskType.md) | The type of task to create. | [optional] 
**initial_metrics** | [**List[NewMetricRequest]**](NewMetricRequest.md) | The initial metrics to apply to agentic tasks. | 
**rules_to_enable** | **List[str]** | The list of rule IDs to enable on the task. | [optional] 
**rules_to_disable** | **List[str]** | The list of rule IDs to disable on the task. | [optional] 
**rules_to_archive** | **List[str]** | The list of rule IDs to archive on the task. | [optional] 
**rules_to_add** | [**List[NewRuleRequest]**](NewRuleRequest.md) | The new rules to add to the task. | [optional] 
**task_id** | **str** | The id of the Shield task to link when creating the new model. | 

## Example

```python
from arthur_client.api_bindings.models.job_spec import JobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of JobSpec from a JSON string
job_spec_instance = JobSpec.from_json(json)
# print the JSON string representation of the object
print(JobSpec.to_json())

# convert the object into a dict
job_spec_dict = job_spec_instance.to_dict()
# create an instance of JobSpec from a dict
job_spec_from_dict = JobSpec.from_dict(job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


