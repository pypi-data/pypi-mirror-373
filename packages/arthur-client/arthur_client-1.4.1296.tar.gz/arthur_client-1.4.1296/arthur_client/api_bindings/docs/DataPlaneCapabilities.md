# DataPlaneCapabilities


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gen_ai_enabled** | **bool** | Field that records if the engine was installed with GenAI capabilities. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.data_plane_capabilities import DataPlaneCapabilities

# TODO update the JSON string below
json = "{}"
# create an instance of DataPlaneCapabilities from a JSON string
data_plane_capabilities_instance = DataPlaneCapabilities.from_json(json)
# print the JSON string representation of the object
print(DataPlaneCapabilities.to_json())

# convert the object into a dict
data_plane_capabilities_dict = data_plane_capabilities_instance.to_dict()
# create an instance of DataPlaneCapabilities from a dict
data_plane_capabilities_from_dict = DataPlaneCapabilities.from_dict(data_plane_capabilities_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


