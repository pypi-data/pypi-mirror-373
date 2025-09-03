# Items


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
from arthur_client.api_bindings.models.items import Items

# TODO update the JSON string below
json = "{}"
# create an instance of Items from a JSON string
items_instance = Items.from_json(json)
# print the JSON string representation of the object
print(Items.to_json())

# convert the object into a dict
items_dict = items_instance.to_dict()
# create an instance of Items from a dict
items_from_dict = Items.from_dict(items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


