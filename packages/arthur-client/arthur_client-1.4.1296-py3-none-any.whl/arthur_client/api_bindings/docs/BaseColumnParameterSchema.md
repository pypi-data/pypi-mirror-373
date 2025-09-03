# BaseColumnParameterSchema


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
**parameter_type** | **str** |  | [optional] [default to 'column']

## Example

```python
from arthur_client.api_bindings.models.base_column_parameter_schema import BaseColumnParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of BaseColumnParameterSchema from a JSON string
base_column_parameter_schema_instance = BaseColumnParameterSchema.from_json(json)
# print the JSON string representation of the object
print(BaseColumnParameterSchema.to_json())

# convert the object into a dict
base_column_parameter_schema_dict = base_column_parameter_schema_instance.to_dict()
# create an instance of BaseColumnParameterSchema from a dict
base_column_parameter_schema_from_dict = BaseColumnParameterSchema.from_dict(base_column_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


