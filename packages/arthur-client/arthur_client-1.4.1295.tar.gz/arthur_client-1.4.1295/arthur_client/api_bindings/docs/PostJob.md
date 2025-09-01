# PostJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kind** | [**PostJobKind**](PostJobKind.md) | Type of job. | 
**job_spec** | [**PostJobSpec**](PostJobSpec.md) |  | 
**schedule_id** | **str** |  | [optional] 
**ready_at** | **datetime** |  | [optional] 
**nonce** | **str** |  | [optional] 
**job_priority** | [**JobPriority**](JobPriority.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_job import PostJob

# TODO update the JSON string below
json = "{}"
# create an instance of PostJob from a JSON string
post_job_instance = PostJob.from_json(json)
# print the JSON string representation of the object
print(PostJob.to_json())

# convert the object into a dict
post_job_dict = post_job_instance.to_dict()
# create an instance of PostJob from a dict
post_job_from_dict = PostJob.from_dict(post_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


