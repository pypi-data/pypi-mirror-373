# PutAvailableDatasets


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available_datasets** | [**List[PutAvailableDataset]**](PutAvailableDataset.md) | List of available datasets to overwrite. | 

## Example

```python
from arthur_client.api_bindings.models.put_available_datasets import PutAvailableDatasets

# TODO update the JSON string below
json = "{}"
# create an instance of PutAvailableDatasets from a JSON string
put_available_datasets_instance = PutAvailableDatasets.from_json(json)
# print the JSON string representation of the object
print(PutAvailableDatasets.to_json())

# convert the object into a dict
put_available_datasets_dict = put_available_datasets_instance.to_dict()
# create an instance of PutAvailableDatasets from a dict
put_available_datasets_from_dict = PutAvailableDatasets.from_dict(put_available_datasets_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


