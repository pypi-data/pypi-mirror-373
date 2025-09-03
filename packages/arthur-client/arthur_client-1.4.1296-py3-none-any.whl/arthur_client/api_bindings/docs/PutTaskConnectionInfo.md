# PutTaskConnectionInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**validation_key** | [**PostTaskValidationAPIKey**](PostTaskValidationAPIKey.md) | The information for the API key with validation permissions for the task. | 
**api_host** | **str** | Host for the task. | 

## Example

```python
from arthur_client.api_bindings.models.put_task_connection_info import PutTaskConnectionInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PutTaskConnectionInfo from a JSON string
put_task_connection_info_instance = PutTaskConnectionInfo.from_json(json)
# print the JSON string representation of the object
print(PutTaskConnectionInfo.to_json())

# convert the object into a dict
put_task_connection_info_dict = put_task_connection_info_instance.to_dict()
# create an instance of PutTaskConnectionInfo from a dict
put_task_connection_info_from_dict = PutTaskConnectionInfo.from_dict(put_task_connection_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


