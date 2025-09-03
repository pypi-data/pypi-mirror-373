# PatchProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_project import PatchProject

# TODO update the JSON string below
json = "{}"
# create an instance of PatchProject from a JSON string
patch_project_instance = PatchProject.from_json(json)
# print the JSON string representation of the object
print(PatchProject.to_json())

# convert the object into a dict
patch_project_dict = patch_project_instance.to_dict()
# create an instance of PatchProject from a dict
patch_project_from_dict = PatchProject.from_dict(patch_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


