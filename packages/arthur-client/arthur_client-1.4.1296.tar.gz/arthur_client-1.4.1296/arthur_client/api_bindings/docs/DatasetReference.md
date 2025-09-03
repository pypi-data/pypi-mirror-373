# DatasetReference


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **str** | ID of the dataset. | 
**dataset_name** | **str** | Name of the dataset. | 
**dataset_connector_type** | [**ConnectorType**](ConnectorType.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.dataset_reference import DatasetReference

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetReference from a JSON string
dataset_reference_instance = DatasetReference.from_json(json)
# print the JSON string representation of the object
print(DatasetReference.to_json())

# convert the object into a dict
dataset_reference_dict = dataset_reference_instance.to_dict()
# create an instance of DatasetReference from a dict
dataset_reference_from_dict = DatasetReference.from_dict(dataset_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


