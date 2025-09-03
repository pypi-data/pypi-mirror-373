# BaseLiteralParameterSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'literal']
**parameter_dtype** | [**DType**](DType.md) | Data type of the parameter. | 

## Example

```python
from arthur_client.api_bindings.models.base_literal_parameter_schema import BaseLiteralParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of BaseLiteralParameterSchema from a JSON string
base_literal_parameter_schema_instance = BaseLiteralParameterSchema.from_json(json)
# print the JSON string representation of the object
print(BaseLiteralParameterSchema.to_json())

# convert the object into a dict
base_literal_parameter_schema_dict = base_literal_parameter_schema_instance.to_dict()
# create an instance of BaseLiteralParameterSchema from a dict
base_literal_parameter_schema_from_dict = BaseLiteralParameterSchema.from_dict(base_literal_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


