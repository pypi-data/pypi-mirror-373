# PutJobState


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_state** | [**JobState**](JobState.md) | JobState to update the job to. | 

## Example

```python
from arthur_client.api_bindings.models.put_job_state import PutJobState

# TODO update the JSON string below
json = "{}"
# create an instance of PutJobState from a JSON string
put_job_state_instance = PutJobState.from_json(json)
# print the JSON string representation of the object
print(PutJobState.to_json())

# convert the object into a dict
put_job_state_dict = put_job_state_instance.to_dict()
# create an instance of PutJobState from a dict
put_job_state_from_dict = PutJobState.from_dict(put_job_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


