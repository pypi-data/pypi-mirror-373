# DatasetLocatorSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fields** | [**List[DatasetLocatorSchemaField]**](DatasetLocatorSchemaField.md) | Schema for dataset locator fields for all datasets using the connector type. | 

## Example

```python
from arthur_client.api_bindings.models.dataset_locator_schema import DatasetLocatorSchema

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetLocatorSchema from a JSON string
dataset_locator_schema_instance = DatasetLocatorSchema.from_json(json)
# print the JSON string representation of the object
print(DatasetLocatorSchema.to_json())

# convert the object into a dict
dataset_locator_schema_dict = dataset_locator_schema_instance.to_dict()
# create an instance of DatasetLocatorSchema from a dict
dataset_locator_schema_from_dict = DatasetLocatorSchema.from_dict(dataset_locator_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


