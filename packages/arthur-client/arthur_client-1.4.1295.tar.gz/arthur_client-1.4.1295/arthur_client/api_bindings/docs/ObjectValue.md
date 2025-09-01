# ObjectValue


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) |  | [optional] [default to []]
**nullable** | **bool** |  | [optional] 
**id** | **str** | Unique ID of the schema node. | [optional] 
**dtype** | [**DType**](DType.md) |  | 
**object** | [**Dict[str, ObjectValue]**](ObjectValue.md) |  | 
**items** | [**Items**](Items.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.object_value import ObjectValue

# TODO update the JSON string below
json = "{}"
# create an instance of ObjectValue from a JSON string
object_value_instance = ObjectValue.from_json(json)
# print the JSON string representation of the object
print(ObjectValue.to_json())

# convert the object into a dict
object_value_dict = object_value_instance.to_dict()
# create an instance of ObjectValue from a dict
object_value_from_dict = ObjectValue.from_dict(object_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


