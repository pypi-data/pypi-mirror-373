# DatasetObjectType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) |  | [optional] [default to []]
**nullable** | **bool** |  | [optional] 
**id** | **str** | Unique ID of the schema node. | [optional] 
**object** | [**Dict[str, ObjectValue]**](ObjectValue.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.dataset_object_type import DatasetObjectType

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetObjectType from a JSON string
dataset_object_type_instance = DatasetObjectType.from_json(json)
# print the JSON string representation of the object
print(DatasetObjectType.to_json())

# convert the object into a dict
dataset_object_type_dict = dataset_object_type_instance.to_dict()
# create an instance of DatasetObjectType from a dict
dataset_object_type_from_dict = DatasetObjectType.from_dict(dataset_object_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


