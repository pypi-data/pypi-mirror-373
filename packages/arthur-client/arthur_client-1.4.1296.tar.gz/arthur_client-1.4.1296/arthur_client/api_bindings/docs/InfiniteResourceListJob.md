# InfiniteResourceListJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Job]**](Job.md) | List of records. | 
**pagination** | [**InfinitePagination**](InfinitePagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.infinite_resource_list_job import InfiniteResourceListJob

# TODO update the JSON string below
json = "{}"
# create an instance of InfiniteResourceListJob from a JSON string
infinite_resource_list_job_instance = InfiniteResourceListJob.from_json(json)
# print the JSON string representation of the object
print(InfiniteResourceListJob.to_json())

# convert the object into a dict
infinite_resource_list_job_dict = infinite_resource_list_job_instance.to_dict()
# create an instance of InfiniteResourceListJob from a dict
infinite_resource_list_job_from_dict = InfiniteResourceListJob.from_dict(infinite_resource_list_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


