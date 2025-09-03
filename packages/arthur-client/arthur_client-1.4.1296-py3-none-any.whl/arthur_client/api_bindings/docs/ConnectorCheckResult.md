# ConnectorCheckResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_check_outcome** | [**ConnectorCheckOutcome**](ConnectorCheckOutcome.md) | Result of the connector check. | 
**failure_reason** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.connector_check_result import ConnectorCheckResult

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorCheckResult from a JSON string
connector_check_result_instance = ConnectorCheckResult.from_json(json)
# print the JSON string representation of the object
print(ConnectorCheckResult.to_json())

# convert the object into a dict
connector_check_result_dict = connector_check_result_instance.to_dict()
# create an instance of ConnectorCheckResult from a dict
connector_check_result_from_dict = ConnectorCheckResult.from_dict(connector_check_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


