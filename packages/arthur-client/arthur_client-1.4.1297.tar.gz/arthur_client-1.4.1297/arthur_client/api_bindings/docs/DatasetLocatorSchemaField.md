# DatasetLocatorSchemaField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of dataset locator field. | 
**d_type** | [**DatasetLocatorFieldDataType**](DatasetLocatorFieldDataType.md) | Data type of the value stored by the field. | 
**is_optional** | **bool** | If field is optional or required. | 
**description** | **str** | Description of dataset locator schema field. | 
**allowed_values** | **List[str]** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.dataset_locator_schema_field import DatasetLocatorSchemaField

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetLocatorSchemaField from a JSON string
dataset_locator_schema_field_instance = DatasetLocatorSchemaField.from_json(json)
# print the JSON string representation of the object
print(DatasetLocatorSchemaField.to_json())

# convert the object into a dict
dataset_locator_schema_field_dict = dataset_locator_schema_field_instance.to_dict()
# create an instance of DatasetLocatorSchemaField from a dict
dataset_locator_schema_field_from_dict = DatasetLocatorSchemaField.from_dict(dataset_locator_schema_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


