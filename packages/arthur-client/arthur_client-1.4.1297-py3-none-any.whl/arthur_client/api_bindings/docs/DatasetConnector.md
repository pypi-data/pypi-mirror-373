# DatasetConnector


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Connector ID associated with the dataset. | 
**name** | **str** | Connector name associated with the dataset. | 
**connector_type** | [**ConnectorType**](ConnectorType.md) | Type of connector associated with the dataset. | 

## Example

```python
from arthur_client.api_bindings.models.dataset_connector import DatasetConnector

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetConnector from a JSON string
dataset_connector_instance = DatasetConnector.from_json(json)
# print the JSON string representation of the object
print(DatasetConnector.to_json())

# convert the object into a dict
dataset_connector_dict = dataset_connector_instance.to_dict()
# create an instance of DatasetConnector from a dict
dataset_connector_from_dict = DatasetConnector.from_dict(dataset_connector_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


