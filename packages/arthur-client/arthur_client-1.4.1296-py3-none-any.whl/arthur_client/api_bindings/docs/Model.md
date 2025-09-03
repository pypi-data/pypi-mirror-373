# Model


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the model. | 
**project_id** | **str** | ID of the parent project. | 
**name** | **str** | Name of the model. | 
**description** | **str** |  | 
**onboarding_identifier** | **str** |  | [optional] 
**last_updated_by_user** | [**User**](User.md) |  | [optional] 
**metric_config** | [**ModelMetricSpec**](ModelMetricSpec.md) | Metric configuration of the model. | 
**schedule** | [**ModelMetricsSchedule**](ModelMetricsSchedule.md) |  | [optional] 
**model_problem_types** | [**List[ModelProblemType]**](ModelProblemType.md) | Unique model problem types of associated datasets. | 
**datasets** | [**List[DatasetReference]**](DatasetReference.md) | Datasets for the model. | 
**data_plane_id** | **str** | ID of the data plane backing this model. | 

## Example

```python
from arthur_client.api_bindings.models.model import Model

# TODO update the JSON string below
json = "{}"
# create an instance of Model from a JSON string
model_instance = Model.from_json(json)
# print the JSON string representation of the object
print(Model.to_json())

# convert the object into a dict
model_dict = model_instance.to_dict()
# create an instance of Model from a dict
model_from_dict = Model.from_dict(model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


