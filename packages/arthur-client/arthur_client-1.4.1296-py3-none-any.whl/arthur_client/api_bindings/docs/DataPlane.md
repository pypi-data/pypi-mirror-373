# DataPlane


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

## Example

```python
from arthur_client.api_bindings.models.data_plane import DataPlane

# TODO update the JSON string below
json = "{}"
# create an instance of DataPlane from a JSON string
data_plane_instance = DataPlane.from_json(json)
# print the JSON string representation of the object
print(DataPlane.to_json())

# convert the object into a dict
data_plane_dict = data_plane_instance.to_dict()
# create an instance of DataPlane from a dict
data_plane_from_dict = DataPlane.from_dict(data_plane_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


