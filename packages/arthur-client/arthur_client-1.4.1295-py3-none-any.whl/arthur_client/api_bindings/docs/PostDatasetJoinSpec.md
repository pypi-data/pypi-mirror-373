# PostDatasetJoinSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**left_dataset_id** | **str** | ID of the first dataset. | 
**right_dataset_id** | **str** | ID of the second dataset. | 
**left_dataset_join_key** | **str** | Column ID from the left dataset to use as a join key. | 
**right_dataset_join_key** | **str** | Column ID from the right dataset to use as a join key. | 
**join_type** | [**DatasetJoinKind**](DatasetJoinKind.md) | Kind of SQL join to perform | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_dataset_join_spec import PostDatasetJoinSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PostDatasetJoinSpec from a JSON string
post_dataset_join_spec_instance = PostDatasetJoinSpec.from_json(json)
# print the JSON string representation of the object
print(PostDatasetJoinSpec.to_json())

# convert the object into a dict
post_dataset_join_spec_dict = post_dataset_join_spec_instance.to_dict()
# create an instance of PostDatasetJoinSpec from a dict
post_dataset_join_spec_from_dict = PostDatasetJoinSpec.from_dict(post_dataset_join_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


