# PostConnectorSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_type** | [**ConnectorType**](ConnectorType.md) | Type of connector. | 
**name** | **str** | Name of connector. | 
**temporary** | **bool** | True if connector is temporary (ie for testing only), false otherwise. | [optional] [default to False]
**fields** | [**List[ConnectorSpecField]**](ConnectorSpecField.md) | List of non-sensitive and sensitive fields for the connector. | 
**data_plane_id** | **str** | ID of the data plane that will execute the connection. Should be formatted as a UUID. | 

## Example

```python
from arthur_client.api_bindings.models.post_connector_spec import PostConnectorSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PostConnectorSpec from a JSON string
post_connector_spec_instance = PostConnectorSpec.from_json(json)
# print the JSON string representation of the object
print(PostConnectorSpec.to_json())

# convert the object into a dict
post_connector_spec_dict = post_connector_spec_instance.to_dict()
# create an instance of PostConnectorSpec from a dict
post_connector_spec_from_dict = PostConnectorSpec.from_dict(post_connector_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


