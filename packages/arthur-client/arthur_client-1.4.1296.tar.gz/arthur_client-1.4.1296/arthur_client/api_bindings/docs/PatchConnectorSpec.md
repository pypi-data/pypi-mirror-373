# PatchConnectorSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**temporary** | **bool** |  | [optional] 
**fields** | [**List[ConnectorSpecField]**](ConnectorSpecField.md) | List of non-sensitive and sensitive fields for the connector. | [optional] [default to []]

## Example

```python
from arthur_client.api_bindings.models.patch_connector_spec import PatchConnectorSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PatchConnectorSpec from a JSON string
patch_connector_spec_instance = PatchConnectorSpec.from_json(json)
# print the JSON string representation of the object
print(PatchConnectorSpec.to_json())

# convert the object into a dict
patch_connector_spec_dict = patch_connector_spec_instance.to_dict()
# create an instance of PatchConnectorSpec from a dict
patch_connector_spec_from_dict = PatchConnectorSpec.from_dict(patch_connector_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


