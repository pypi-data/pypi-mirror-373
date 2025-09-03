# PatchModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**dataset_ids** | **List[str]** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_model import PatchModel

# TODO update the JSON string below
json = "{}"
# create an instance of PatchModel from a JSON string
patch_model_instance = PatchModel.from_json(json)
# print the JSON string representation of the object
print(PatchModel.to_json())

# convert the object into a dict
patch_model_dict = patch_model_instance.to_dict()
# create an instance of PatchModel from a dict
patch_model_from_dict = PatchModel.from_dict(patch_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


