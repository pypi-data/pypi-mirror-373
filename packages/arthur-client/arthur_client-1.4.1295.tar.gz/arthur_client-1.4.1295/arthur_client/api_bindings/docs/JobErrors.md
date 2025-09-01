# JobErrors


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[JobError]**](JobError.md) | List of errors encountered during the job execution. | 

## Example

```python
from arthur_client.api_bindings.models.job_errors import JobErrors

# TODO update the JSON string below
json = "{}"
# create an instance of JobErrors from a JSON string
job_errors_instance = JobErrors.from_json(json)
# print the JSON string representation of the object
print(JobErrors.to_json())

# convert the object into a dict
job_errors_dict = job_errors_instance.to_dict()
# create an instance of JobErrors from a dict
job_errors_from_dict = JobErrors.from_dict(job_errors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


