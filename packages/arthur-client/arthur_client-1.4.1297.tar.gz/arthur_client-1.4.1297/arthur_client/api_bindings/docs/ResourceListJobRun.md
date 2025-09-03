# ResourceListJobRun


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[JobRun]**](JobRun.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_job_run import ResourceListJobRun

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListJobRun from a JSON string
resource_list_job_run_instance = ResourceListJobRun.from_json(json)
# print the JSON string representation of the object
print(ResourceListJobRun.to_json())

# convert the object into a dict
resource_list_job_run_dict = resource_list_job_run_instance.to_dict()
# create an instance of ResourceListJobRun from a dict
resource_list_job_run_from_dict = ResourceListJobRun.from_dict(resource_list_job_run_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


