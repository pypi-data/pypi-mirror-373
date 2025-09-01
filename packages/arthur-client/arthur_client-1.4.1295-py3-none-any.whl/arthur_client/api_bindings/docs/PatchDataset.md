# PatchDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**dataset_locator** | [**PatchDatasetLocator**](PatchDatasetLocator.md) |  | [optional] 
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_dataset import PatchDataset

# TODO update the JSON string below
json = "{}"
# create an instance of PatchDataset from a JSON string
patch_dataset_instance = PatchDataset.from_json(json)
# print the JSON string representation of the object
print(PatchDataset.to_json())

# convert the object into a dict
patch_dataset_dict = patch_dataset_instance.to_dict()
# create an instance of PatchDataset from a dict
patch_dataset_from_dict = PatchDataset.from_dict(patch_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


