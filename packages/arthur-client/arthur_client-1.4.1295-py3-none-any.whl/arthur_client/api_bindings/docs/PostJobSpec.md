# PostJobSpec

Job specification for the job kind.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'alert_check']
**scope_model_id** | **str** | The id of the model to check alerts. | 
**start_timestamp** | **datetime** | Inclusive timestamp marking the start of the job series. | 
**end_timestamp** | **datetime** | The end timestamp to use for fetching data. | 
**connector_id** | **str** | The id of the connector to list datasets. | 
**available_dataset_id** | **str** | The id of the dataset within the connector to inspect the schema. | 
**check_range_start_timestamp** | **datetime** | The start timestamp to use for checking the alerts on the data. | 
**check_range_end_timestamp** | **datetime** | The end timestamp to use for checking the alerts on the data. | 

## Example

```python
from arthur_client.api_bindings.models.post_job_spec import PostJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PostJobSpec from a JSON string
post_job_spec_instance = PostJobSpec.from_json(json)
# print the JSON string representation of the object
print(PostJobSpec.to_json())

# convert the object into a dict
post_job_spec_dict = post_job_spec_instance.to_dict()
# create an instance of PostJobSpec from a dict
post_job_spec_from_dict = PostJobSpec.from_dict(post_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


