# PutAvailableDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**dataset_locator** | [**DatasetLocator**](DatasetLocator.md) |  | [optional] 
**dataset_schema** | [**PutDatasetSchema**](PutDatasetSchema.md) |  | [optional] 
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 
**dataset_join_spec** | [**PostDatasetJoinSpec**](PostDatasetJoinSpec.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.put_available_dataset import PutAvailableDataset

# TODO update the JSON string below
json = "{}"
# create an instance of PutAvailableDataset from a JSON string
put_available_dataset_instance = PutAvailableDataset.from_json(json)
# print the JSON string representation of the object
print(PutAvailableDataset.to_json())

# convert the object into a dict
put_available_dataset_dict = put_available_dataset_instance.to_dict()
# create an instance of PutAvailableDataset from a dict
put_available_dataset_from_dict = PutAvailableDataset.from_dict(put_available_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


