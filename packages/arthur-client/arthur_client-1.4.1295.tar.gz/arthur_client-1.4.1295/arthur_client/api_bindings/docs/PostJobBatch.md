# PostJobBatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jobs** | [**List[PostJob]**](PostJob.md) | List of jobs to create. | 

## Example

```python
from arthur_client.api_bindings.models.post_job_batch import PostJobBatch

# TODO update the JSON string below
json = "{}"
# create an instance of PostJobBatch from a JSON string
post_job_batch_instance = PostJobBatch.from_json(json)
# print the JSON string representation of the object
print(PostJobBatch.to_json())

# convert the object into a dict
post_job_batch_dict = post_job_batch_instance.to_dict()
# create an instance of PostJobBatch from a dict
post_job_batch_from_dict = PostJobBatch.from_dict(post_job_batch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


