# ResourceListJobError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[JobError]**](JobError.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_job_error import ResourceListJobError

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListJobError from a JSON string
resource_list_job_error_instance = ResourceListJobError.from_json(json)
# print the JSON string representation of the object
print(ResourceListJobError.to_json())

# convert the object into a dict
resource_list_job_error_dict = resource_list_job_error_instance.to_dict()
# create an instance of ResourceListJobError from a dict
resource_list_job_error_from_dict = ResourceListJobError.from_dict(resource_list_job_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


