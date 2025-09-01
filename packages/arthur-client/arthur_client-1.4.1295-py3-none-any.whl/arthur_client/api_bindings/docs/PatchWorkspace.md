# PatchWorkspace


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the workspace. | 

## Example

```python
from arthur_client.api_bindings.models.patch_workspace import PatchWorkspace

# TODO update the JSON string below
json = "{}"
# create an instance of PatchWorkspace from a JSON string
patch_workspace_instance = PatchWorkspace.from_json(json)
# print the JSON string representation of the object
print(PatchWorkspace.to_json())

# convert the object into a dict
patch_workspace_dict = patch_workspace_instance.to_dict()
# create an instance of PatchWorkspace from a dict
patch_workspace_from_dict = PatchWorkspace.from_dict(patch_workspace_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


