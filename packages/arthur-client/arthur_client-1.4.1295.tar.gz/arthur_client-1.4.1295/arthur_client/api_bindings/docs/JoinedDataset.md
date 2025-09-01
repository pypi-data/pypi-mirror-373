# JoinedDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of dataset. | 
**name** | **str** |  | 
**column_id** | **str** | Column ID to use as the join key. | 
**column_name** | **str** | Name of column used as join key. | 

## Example

```python
from arthur_client.api_bindings.models.joined_dataset import JoinedDataset

# TODO update the JSON string below
json = "{}"
# create an instance of JoinedDataset from a JSON string
joined_dataset_instance = JoinedDataset.from_json(json)
# print the JSON string representation of the object
print(JoinedDataset.to_json())

# convert the object into a dict
joined_dataset_dict = joined_dataset_instance.to_dict()
# create an instance of JoinedDataset from a dict
joined_dataset_from_dict = JoinedDataset.from_dict(joined_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


