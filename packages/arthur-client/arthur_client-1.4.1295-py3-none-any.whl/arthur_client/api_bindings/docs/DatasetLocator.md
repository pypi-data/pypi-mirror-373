# DatasetLocator


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fields** | [**List[DatasetLocatorField]**](DatasetLocatorField.md) | Fields directing to the location of the dataset within the connector. Schema defined on connector schema. | 

## Example

```python
from arthur_client.api_bindings.models.dataset_locator import DatasetLocator

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetLocator from a JSON string
dataset_locator_instance = DatasetLocator.from_json(json)
# print the JSON string representation of the object
print(DatasetLocator.to_json())

# convert the object into a dict
dataset_locator_dict = dataset_locator_instance.to_dict()
# create an instance of DatasetLocator from a dict
dataset_locator_from_dict = DatasetLocator.from_dict(dataset_locator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


