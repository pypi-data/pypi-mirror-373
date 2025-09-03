# BaseDatasetParameterSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parameter_key** | **str** | Name of the parameter. | 
**friendly_name** | **str** | User facing name of the parameter. | 
**description** | **str** | Description of the parameter. | 
**parameter_type** | **str** |  | [optional] [default to 'dataset']
**model_problem_type** | [**ModelProblemType**](ModelProblemType.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.base_dataset_parameter_schema import BaseDatasetParameterSchema

# TODO update the JSON string below
json = "{}"
# create an instance of BaseDatasetParameterSchema from a JSON string
base_dataset_parameter_schema_instance = BaseDatasetParameterSchema.from_json(json)
# print the JSON string representation of the object
print(BaseDatasetParameterSchema.to_json())

# convert the object into a dict
base_dataset_parameter_schema_dict = base_dataset_parameter_schema_instance.to_dict()
# create an instance of BaseDatasetParameterSchema from a dict
base_dataset_parameter_schema_from_dict = BaseDatasetParameterSchema.from_dict(base_dataset_parameter_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


