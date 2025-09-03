# PostModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the model. | 
**description** | **str** |  | [optional] 
**onboarding_identifier** | **str** |  | [optional] 
**metric_config** | [**PutModelMetricSpec**](PutModelMetricSpec.md) |  | [optional] 
**dataset_ids** | **List[str]** | IDs of datasets for the model. | 

## Example

```python
from arthur_client.api_bindings.models.post_model import PostModel

# TODO update the JSON string below
json = "{}"
# create an instance of PostModel from a JSON string
post_model_instance = PostModel.from_json(json)
# print the JSON string representation of the object
print(PostModel.to_json())

# convert the object into a dict
post_model_dict = post_model_instance.to_dict()
# create an instance of PostModel from a dict
post_model_from_dict = PostModel.from_dict(post_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


