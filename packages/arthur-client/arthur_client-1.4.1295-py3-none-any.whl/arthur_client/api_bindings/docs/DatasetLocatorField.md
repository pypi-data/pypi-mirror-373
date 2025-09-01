# DatasetLocatorField


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Name of dataset locator field. | 
**value** | **str** | Value of dataset locator field. | 

## Example

```python
from arthur_client.api_bindings.models.dataset_locator_field import DatasetLocatorField

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetLocatorField from a JSON string
dataset_locator_field_instance = DatasetLocatorField.from_json(json)
# print the JSON string representation of the object
print(DatasetLocatorField.to_json())

# convert the object into a dict
dataset_locator_field_dict = dataset_locator_field_instance.to_dict()
# create an instance of DatasetLocatorField from a dict
dataset_locator_field_from_dict = DatasetLocatorField.from_dict(dataset_locator_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


