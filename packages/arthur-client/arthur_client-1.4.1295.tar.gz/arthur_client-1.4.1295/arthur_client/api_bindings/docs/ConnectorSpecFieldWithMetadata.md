# ConnectorSpecFieldWithMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Name of connector field. | 
**value** | **str** | Value of connector field. | 
**d_type** | [**ConnectorFieldDataType**](ConnectorFieldDataType.md) | Data type of connector field. | 
**is_sensitive** | **bool** | Whether or not this is a sensitive field. | 

## Example

```python
from arthur_client.api_bindings.models.connector_spec_field_with_metadata import ConnectorSpecFieldWithMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorSpecFieldWithMetadata from a JSON string
connector_spec_field_with_metadata_instance = ConnectorSpecFieldWithMetadata.from_json(json)
# print the JSON string representation of the object
print(ConnectorSpecFieldWithMetadata.to_json())

# convert the object into a dict
connector_spec_field_with_metadata_dict = connector_spec_field_with_metadata_instance.to_dict()
# create an instance of ConnectorSpecFieldWithMetadata from a dict
connector_spec_field_with_metadata_from_dict = ConnectorSpecFieldWithMetadata.from_dict(connector_spec_field_with_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


