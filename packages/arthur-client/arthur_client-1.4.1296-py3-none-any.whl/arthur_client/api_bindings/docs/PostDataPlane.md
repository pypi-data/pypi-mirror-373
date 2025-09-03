# PostDataPlane


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of data plane. | 
**description** | **str** | Description of data plane. | 
**capabilities** | [**DataPlaneCapabilities**](DataPlaneCapabilities.md) | Capabilities for this data plane. | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_data_plane import PostDataPlane

# TODO update the JSON string below
json = "{}"
# create an instance of PostDataPlane from a JSON string
post_data_plane_instance = PostDataPlane.from_json(json)
# print the JSON string representation of the object
print(PostDataPlane.to_json())

# convert the object into a dict
post_data_plane_dict = post_data_plane_instance.to_dict()
# create an instance of PostDataPlane from a dict
post_data_plane_from_dict = PostDataPlane.from_dict(post_data_plane_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


