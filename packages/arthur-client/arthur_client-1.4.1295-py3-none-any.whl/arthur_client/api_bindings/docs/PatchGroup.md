# PatchGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_group import PatchGroup

# TODO update the JSON string below
json = "{}"
# create an instance of PatchGroup from a JSON string
patch_group_instance = PatchGroup.from_json(json)
# print the JSON string representation of the object
print(PatchGroup.to_json())

# convert the object into a dict
patch_group_dict = patch_group_instance.to_dict()
# create an instance of PatchGroup from a dict
patch_group_from_dict = PatchGroup.from_dict(patch_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


