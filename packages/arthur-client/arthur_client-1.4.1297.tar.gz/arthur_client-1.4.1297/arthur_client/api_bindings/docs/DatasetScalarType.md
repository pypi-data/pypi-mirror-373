# DatasetScalarType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) |  | [optional] [default to []]
**nullable** | **bool** |  | [optional] 
**id** | **str** | Unique ID of the schema node. | [optional] 
**dtype** | [**DType**](DType.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.dataset_scalar_type import DatasetScalarType

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetScalarType from a JSON string
dataset_scalar_type_instance = DatasetScalarType.from_json(json)
# print the JSON string representation of the object
print(DatasetScalarType.to_json())

# convert the object into a dict
dataset_scalar_type_dict = dataset_scalar_type_instance.to_dict()
# create an instance of DatasetScalarType from a dict
dataset_scalar_type_from_dict = DatasetScalarType.from_dict(dataset_scalar_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


