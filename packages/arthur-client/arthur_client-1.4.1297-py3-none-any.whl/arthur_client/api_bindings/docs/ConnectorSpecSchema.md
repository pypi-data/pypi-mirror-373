# ConnectorSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**connector_type** | [**ConnectorType**](ConnectorType.md) | Connector type for the schema. Must be unique. | 
**fields** | [**List[ConnectorSpecSchemaField]**](ConnectorSpecSchemaField.md) | Metadata for optional and required connector fields. | 
**dataset_locator_schema** | [**DatasetLocatorSchema**](DatasetLocatorSchema.md) | Schema with dataset locator metadata for all datasets using the connector type. | 
**supports_dataset_listing** | **bool** | Indicates whether this connector supports listing available datasets. | 

## Example

```python
from arthur_client.api_bindings.models.connector_spec_schema import ConnectorSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorSpecSchema from a JSON string
connector_spec_schema_instance = ConnectorSpecSchema.from_json(json)
# print the JSON string representation of the object
print(ConnectorSpecSchema.to_json())

# convert the object into a dict
connector_spec_schema_dict = connector_spec_schema_instance.to_dict()
# create an instance of ConnectorSpecSchema from a dict
connector_spec_schema_from_dict = ConnectorSpecSchema.from_dict(connector_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


