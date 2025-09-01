# MetricsDatasetParameterSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'dataset']
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 
**optional** | **bool** | Boolean denoting if the parameter is optional. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.metrics_dataset_parameter_schema import MetricsDatasetParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsDatasetParameterSchema from a JSON string
metrics_dataset_parameter_schema_instance = MetricsDatasetParameterSchema.from_json(json)
# print the JSON string representation of the object
print(MetricsDatasetParameterSchema.to_json())

# convert the object into a dict
metrics_dataset_parameter_schema_dict = metrics_dataset_parameter_schema_instance.to_dict()
# create an instance of MetricsDatasetParameterSchema from a dict
metrics_dataset_parameter_schema_from_dict = MetricsDatasetParameterSchema.from_dict(metrics_dataset_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


