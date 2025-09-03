# DatasetColumn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique ID of the column. | [optional] 
**source_name** | **str** |  | 
**definition** | [**Definition**](Definition.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.dataset_column import DatasetColumn

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetColumn from a JSON string
dataset_column_instance = DatasetColumn.from_json(json)
# print the JSON string representation of the object
print(DatasetColumn.to_json())

# convert the object into a dict
dataset_column_dict = dataset_column_instance.to_dict()
# create an instance of DatasetColumn from a dict
dataset_column_from_dict = DatasetColumn.from_dict(dataset_column_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


