# ConnectorPaginationOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** |  | [optional] [default to 1]
**page_size** | **int** |  | [optional] [default to 25]

## Example

```python
from arthur_client.api_bindings.models.connector_pagination_options import ConnectorPaginationOptions

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorPaginationOptions from a JSON string
connector_pagination_options_instance = ConnectorPaginationOptions.from_json(json)
# print the JSON string representation of the object
print(ConnectorPaginationOptions.to_json())

# convert the object into a dict
connector_pagination_options_dict = connector_pagination_options_instance.to_dict()
# create an instance of ConnectorPaginationOptions from a dict
connector_pagination_options_from_dict = ConnectorPaginationOptions.from_dict(connector_pagination_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


