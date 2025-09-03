# DatasetJoinSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**left_joined_dataset** | [**JoinedDataset**](JoinedDataset.md) | Left dataset in the join. | 
**right_joined_dataset** | [**JoinedDataset**](JoinedDataset.md) | Right dataset in the join. | 
**join_type** | [**DatasetJoinKind**](DatasetJoinKind.md) | Kind of SQL join to perform | [optional] 

## Example

```python
from arthur_client.api_bindings.models.dataset_join_spec import DatasetJoinSpec

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetJoinSpec from a JSON string
dataset_join_spec_instance = DatasetJoinSpec.from_json(json)
# print the JSON string representation of the object
print(DatasetJoinSpec.to_json())

# convert the object into a dict
dataset_join_spec_dict = dataset_join_spec_instance.to_dict()
# create an instance of DatasetJoinSpec from a dict
dataset_join_spec_from_dict = DatasetJoinSpec.from_dict(dataset_join_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


