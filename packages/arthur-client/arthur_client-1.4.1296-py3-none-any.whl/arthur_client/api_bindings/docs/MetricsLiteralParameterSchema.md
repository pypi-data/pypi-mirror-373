# MetricsLiteralParameterSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'literal']
**parameter_dtype** | [**DType**](DType.md) | Data type of the parameter. | 
**optional** | **bool** | Boolean denoting if the parameter is optional. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.metrics_literal_parameter_schema import MetricsLiteralParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsLiteralParameterSchema from a JSON string
metrics_literal_parameter_schema_instance = MetricsLiteralParameterSchema.from_json(json)
# print the JSON string representation of the object
print(MetricsLiteralParameterSchema.to_json())

# convert the object into a dict
metrics_literal_parameter_schema_dict = metrics_literal_parameter_schema_instance.to_dict()
# create an instance of MetricsLiteralParameterSchema from a dict
metrics_literal_parameter_schema_from_dict = MetricsLiteralParameterSchema.from_dict(metrics_literal_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


