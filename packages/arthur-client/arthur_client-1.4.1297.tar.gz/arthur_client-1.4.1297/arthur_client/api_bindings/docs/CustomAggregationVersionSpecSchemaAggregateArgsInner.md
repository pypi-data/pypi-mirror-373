# CustomAggregationVersionSpecSchemaAggregateArgsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'column']
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 
**parameter_dtype** | [**DType**](DType.md) | Data type of the parameter. | 
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) | List of tags that are applicable to this parameter. Datasets with columns that have matching tags can be inferred this way. | [optional] [default to []]
**source_dataset_parameter_key** | **str** | Name of the parameter that provides the dataset to be used for this column. | 
**allowed_column_types** | [**List[BaseColumnParameterSchemaAllowedColumnTypesInner]**](BaseColumnParameterSchemaAllowedColumnTypesInner.md) |  | [optional] 
**allow_any_column_type** | **bool** | Indicates if this metric parameter can accept any column type. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.custom_aggregation_version_spec_schema_aggregate_args_inner import CustomAggregationVersionSpecSchemaAggregateArgsInner

# TODO update the JSON string below
json = "{}"
# create an instance of CustomAggregationVersionSpecSchemaAggregateArgsInner from a JSON string
custom_aggregation_version_spec_schema_aggregate_args_inner_instance = CustomAggregationVersionSpecSchemaAggregateArgsInner.from_json(json)
# print the JSON string representation of the object
print(CustomAggregationVersionSpecSchemaAggregateArgsInner.to_json())

# convert the object into a dict
custom_aggregation_version_spec_schema_aggregate_args_inner_dict = custom_aggregation_version_spec_schema_aggregate_args_inner_instance.to_dict()
# create an instance of CustomAggregationVersionSpecSchemaAggregateArgsInner from a dict
custom_aggregation_version_spec_schema_aggregate_args_inner_from_dict = CustomAggregationVersionSpecSchemaAggregateArgsInner.from_dict(custom_aggregation_version_spec_schema_aggregate_args_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


