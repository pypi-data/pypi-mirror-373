# DatasetSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alias_mask** | **Dict[str, str]** |  | 
**columns** | [**List[DatasetColumn]**](DatasetColumn.md) |  | 
**column_names** | **Dict[str, str]** |  | [readonly] 

## Example

```python
from arthur_client.api_bindings.models.dataset_schema import DatasetSchema

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetSchema from a JSON string
dataset_schema_instance = DatasetSchema.from_json(json)
# print the JSON string representation of the object
print(DatasetSchema.to_json())

# convert the object into a dict
dataset_schema_dict = dataset_schema_instance.to_dict()
# create an instance of DatasetSchema from a dict
dataset_schema_from_dict = DatasetSchema.from_dict(dataset_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


