# ResourceListJobLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[JobLog]**](JobLog.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_job_log import ResourceListJobLog

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListJobLog from a JSON string
resource_list_job_log_instance = ResourceListJobLog.from_json(json)
# print the JSON string representation of the object
print(ResourceListJobLog.to_json())

# convert the object into a dict
resource_list_job_log_dict = resource_list_job_log_instance.to_dict()
# create an instance of ResourceListJobLog from a dict
resource_list_job_log_from_dict = ResourceListJobLog.from_dict(resource_list_job_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


