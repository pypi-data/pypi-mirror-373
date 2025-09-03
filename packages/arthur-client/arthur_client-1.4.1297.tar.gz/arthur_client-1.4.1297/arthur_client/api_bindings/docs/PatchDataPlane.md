# PatchDataPlane


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**capabilities** | [**PatchDataPlaneCapabilities**](PatchDataPlaneCapabilities.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_data_plane import PatchDataPlane

# TODO update the JSON string below
json = "{}"
# create an instance of PatchDataPlane from a JSON string
patch_data_plane_instance = PatchDataPlane.from_json(json)
# print the JSON string representation of the object
print(PatchDataPlane.to_json())

# convert the object into a dict
patch_data_plane_dict = patch_data_plane_instance.to_dict()
# create an instance of PatchDataPlane from a dict
patch_data_plane_from_dict = PatchDataPlane.from_dict(patch_data_plane_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


