# SensitiveDataPlane


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the data plane. | 
**name** | **str** | Name of data plane. | 
**workspace_id** | **str** | ID of the parent workspace. | 
**description** | **str** | Description of data plane. | 
**user_id** | **str** | ID of the data plane&#39;s underlying user. | 
**last_check_in_time** | **datetime** |  | 
**capabilities** | [**DataPlaneCapabilities**](DataPlaneCapabilities.md) | Capabilities for this data plane. | 
**client_id** | **str** | ID of the auth client. | 
**client_secret** | **str** | Auth client secret. | 

## Example

```python
from arthur_client.api_bindings.models.sensitive_data_plane import SensitiveDataPlane

# TODO update the JSON string below
json = "{}"
# create an instance of SensitiveDataPlane from a JSON string
sensitive_data_plane_instance = SensitiveDataPlane.from_json(json)
# print the JSON string representation of the object
print(SensitiveDataPlane.to_json())

# convert the object into a dict
sensitive_data_plane_dict = sensitive_data_plane_instance.to_dict()
# create an instance of SensitiveDataPlane from a dict
sensitive_data_plane_from_dict = SensitiveDataPlane.from_dict(sensitive_data_plane_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


