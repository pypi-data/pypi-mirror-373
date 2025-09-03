# DatasetListType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag_hints** | [**List[ScopeSchemaTag]**](ScopeSchemaTag.md) |  | [optional] [default to []]
**nullable** | **bool** |  | [optional] 
**id** | **str** | Unique ID of the schema node. | [optional] 
**items** | [**Items**](Items.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.dataset_list_type import DatasetListType

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetListType from a JSON string
dataset_list_type_instance = DatasetListType.from_json(json)
# print the JSON string representation of the object
print(DatasetListType.to_json())

# convert the object into a dict
dataset_list_type_dict = dataset_list_type_instance.to_dict()
# create an instance of DatasetListType from a dict
dataset_list_type_from_dict = DatasetListType.from_dict(dataset_list_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


