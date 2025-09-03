# Dataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | Unique ID of the dataset. | 
**name** | **str** |  | [optional] 
**dataset_locator** | [**DatasetLocator**](DatasetLocator.md) |  | 
**dataset_schema** | [**DatasetSchema**](DatasetSchema.md) | Schema definition of the dataset. | 
**data_plane_id** | **str** | ID of the data plane backing this dataset. | 
**connector** | [**DatasetConnector**](DatasetConnector.md) |  | [optional] 
**project_id** | **str** | ID of parent project. | 
**join_spec** | [**DatasetJoinSpec**](DatasetJoinSpec.md) |  | [optional] 
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) | Model problem type associated with the dataset. | 

## Example

```python
from arthur_client.api_bindings.models.dataset import Dataset

# TODO update the JSON string below
json = "{}"
# create an instance of Dataset from a JSON string
dataset_instance = Dataset.from_json(json)
# print the JSON string representation of the object
print(Dataset.to_json())

# convert the object into a dict
dataset_dict = dataset_instance.to_dict()
# create an instance of Dataset from a dict
dataset_from_dict = Dataset.from_dict(dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


