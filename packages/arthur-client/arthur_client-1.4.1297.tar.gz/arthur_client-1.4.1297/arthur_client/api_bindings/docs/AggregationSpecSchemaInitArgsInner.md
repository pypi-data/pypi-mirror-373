# AggregationSpecSchemaInitArgsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'column_list']
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 
**optional** | **bool** | Boolean denoting if the parameter is optional. | [optional] [default to False]
**parameter_dtype** | [**DType**](DType.md) | Data type of the parameter. | 
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) | List of tags that are applicable to this parameter. Datasets with columns that have matching tags can be inferred this way. | [optional] [default to []]
**source_dataset_parameter_key** | **str** | Name of the parameter that provides the dataset to be used for this column. | 
**allowed_column_types** | [**List[BaseColumnParameterSchemaAllowedColumnTypesInner]**](BaseColumnParameterSchemaAllowedColumnTypesInner.md) |  | [optional] 
**allow_any_column_type** | **bool** | Indicates if this metric parameter can accept any column type. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.aggregation_spec_schema_init_args_inner import AggregationSpecSchemaInitArgsInner

# TODO update the JSON string below
json = "{}"
# create an instance of AggregationSpecSchemaInitArgsInner from a JSON string
aggregation_spec_schema_init_args_inner_instance = AggregationSpecSchemaInitArgsInner.from_json(json)
# print the JSON string representation of the object
print(AggregationSpecSchemaInitArgsInner.to_json())

# convert the object into a dict
aggregation_spec_schema_init_args_inner_dict = aggregation_spec_schema_init_args_inner_instance.to_dict()
# create an instance of AggregationSpecSchemaInitArgsInner from a dict
aggregation_spec_schema_init_args_inner_from_dict = AggregationSpecSchemaInitArgsInner.from_dict(aggregation_spec_schema_init_args_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


