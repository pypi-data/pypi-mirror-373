# ScalarType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dtype** | [**DType**](DType.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.scalar_type import ScalarType

# TODO update the JSON string below
json = "{}"
# create an instance of ScalarType from a JSON string
scalar_type_instance = ScalarType.from_json(json)
# print the JSON string representation of the object
print(ScalarType.to_json())

# convert the object into a dict
scalar_type_dict = scalar_type_instance.to_dict()
# create an instance of ScalarType from a dict
scalar_type_from_dict = ScalarType.from_dict(scalar_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


