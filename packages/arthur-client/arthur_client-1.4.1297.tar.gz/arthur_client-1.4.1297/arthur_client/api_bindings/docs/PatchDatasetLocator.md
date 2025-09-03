# PatchDatasetLocator


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fields** | [**List[DatasetLocatorField]**](DatasetLocatorField.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.patch_dataset_locator import PatchDatasetLocator

# TODO update the JSON string below
json = "{}"
# create an instance of PatchDatasetLocator from a JSON string
patch_dataset_locator_instance = PatchDatasetLocator.from_json(json)
# print the JSON string representation of the object
print(PatchDatasetLocator.to_json())

# convert the object into a dict
patch_dataset_locator_dict = patch_dataset_locator_instance.to_dict()
# create an instance of PatchDatasetLocator from a dict
patch_dataset_locator_from_dict = PatchDatasetLocator.from_dict(patch_dataset_locator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


