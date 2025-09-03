# PostDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**dataset_locator** | [**DatasetLocator**](DatasetLocator.md) |  | [optional] 
**dataset_schema** | [**PutDatasetSchema**](PutDatasetSchema.md) |  | [optional] 
**dataset_join_spec** | [**PostDatasetJoinSpec**](PostDatasetJoinSpec.md) |  | [optional] 
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) | Model problem type associated with the dataset. | 

## Example

```python
from arthur_client.api_bindings.models.post_dataset import PostDataset

# TODO update the JSON string below
json = "{}"
# create an instance of PostDataset from a JSON string
post_dataset_instance = PostDataset.from_json(json)
# print the JSON string representation of the object
print(PostDataset.to_json())

# convert the object into a dict
post_dataset_dict = post_dataset_instance.to_dict()
# create an instance of PostDataset from a dict
post_dataset_from_dict = PostDataset.from_dict(post_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


