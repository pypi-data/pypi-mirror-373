# ConnectorSpecField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Name of connector field. | 
**value** | **str** | Value of connector field. | 

## Example

```python
from arthur_client.api_bindings.models.connector_spec_field import ConnectorSpecField

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorSpecField from a JSON string
connector_spec_field_instance = ConnectorSpecField.from_json(json)
# print the JSON string representation of the object
print(ConnectorSpecField.to_json())

# convert the object into a dict
connector_spec_field_dict = connector_spec_field_instance.to_dict()
# create an instance of ConnectorSpecField from a dict
connector_spec_field_from_dict = ConnectorSpecField.from_dict(connector_spec_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


