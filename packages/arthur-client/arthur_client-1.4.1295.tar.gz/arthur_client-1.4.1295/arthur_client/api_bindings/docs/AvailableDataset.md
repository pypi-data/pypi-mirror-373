# AvailableDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | Unique ID of the available dataset. | 
**connector_id** | **str** |  | [optional] 
**project_id** | **str** | ID of parent project. | 
**name** | **str** |  | [optional] 
**data_plane_id** | **str** | ID of the data plane backing this dataset. | 
**dataset_locator** | [**DatasetLocator**](DatasetLocator.md) |  | [optional] 
**dataset_schema** | [**DatasetSchema**](DatasetSchema.md) |  | [optional] 
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 
**join_spec** | [**DatasetJoinSpec**](DatasetJoinSpec.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.available_dataset import AvailableDataset

# TODO update the JSON string below
json = "{}"
# create an instance of AvailableDataset from a JSON string
available_dataset_instance = AvailableDataset.from_json(json)
# print the JSON string representation of the object
print(AvailableDataset.to_json())

# convert the object into a dict
available_dataset_dict = available_dataset_instance.to_dict()
# create an instance of AvailableDataset from a dict
available_dataset_from_dict = AvailableDataset.from_dict(available_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


