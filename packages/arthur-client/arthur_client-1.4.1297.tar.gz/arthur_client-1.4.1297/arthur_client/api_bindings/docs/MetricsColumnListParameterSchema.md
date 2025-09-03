# MetricsColumnListParameterSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) | List of tags that are applicable to this parameter. Datasets with columns that have matching tags can be inferred this way. | [optional] [default to []]
**source_dataset_parameter_key** | **str** | Name of the parameter that provides the dataset to be used for this column. | 
**allowed_column_types** | [**List[BaseColumnParameterSchemaAllowedColumnTypesInner]**](BaseColumnParameterSchemaAllowedColumnTypesInner.md) |  | [optional] 
**allow_any_column_type** | **bool** | Indicates if this metric parameter can accept any column type. | [optional] [default to False]
**optional** | **bool** | Boolean denoting if the parameter is optional. | [optional] [default to False]
**parameter_type** | **str** |  | [optional] [default to 'column_list']

## Example

```python
from arthur_client.api_bindings.models.metrics_column_list_parameter_schema import MetricsColumnListParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsColumnListParameterSchema from a JSON string
metrics_column_list_parameter_schema_instance = MetricsColumnListParameterSchema.from_json(json)
# print the JSON string representation of the object
print(MetricsColumnListParameterSchema.to_json())

# convert the object into a dict
metrics_column_list_parameter_schema_dict = metrics_column_list_parameter_schema_instance.to_dict()
# create an instance of MetricsColumnListParameterSchema from a dict
metrics_column_list_parameter_schema_from_dict = MetricsColumnListParameterSchema.from_dict(metrics_column_list_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


