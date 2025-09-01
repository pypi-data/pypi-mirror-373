# ConnectorSpecSchemaField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of connector field. | 
**is_sensitive** | **bool** | If field stores sensitive data. | 
**is_optional** | **bool** | If field is optional or required. | 
**d_type** | [**ConnectorFieldDataType**](ConnectorFieldDataType.md) | Data type of the value stored by the field. | 
**description** | **str** | Description of connector field. | 
**allowed_values** | **List[str]** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.connector_spec_schema_field import ConnectorSpecSchemaField

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorSpecSchemaField from a JSON string
connector_spec_schema_field_instance = ConnectorSpecSchemaField.from_json(json)
# print the JSON string representation of the object
print(ConnectorSpecSchemaField.to_json())

# convert the object into a dict
connector_spec_schema_field_dict = connector_spec_schema_field_instance.to_dict()
# create an instance of ConnectorSpecSchemaField from a dict
connector_spec_schema_field_from_dict = ConnectorSpecSchemaField.from_dict(connector_spec_schema_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


