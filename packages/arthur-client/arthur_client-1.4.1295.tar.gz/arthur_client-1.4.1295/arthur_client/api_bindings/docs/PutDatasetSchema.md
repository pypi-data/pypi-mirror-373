# PutDatasetSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alias_mask** | **Dict[str, str]** |  | 
**columns** | [**List[DatasetColumn]**](DatasetColumn.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.put_dataset_schema import PutDatasetSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PutDatasetSchema from a JSON string
put_dataset_schema_instance = PutDatasetSchema.from_json(json)
# print the JSON string representation of the object
print(PutDatasetSchema.to_json())

# convert the object into a dict
put_dataset_schema_dict = put_dataset_schema_instance.to_dict()
# create an instance of PutDatasetSchema from a dict
put_dataset_schema_from_dict = PutDatasetSchema.from_dict(put_dataset_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


