# ResourceListAvailableDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[AvailableDataset]**](AvailableDataset.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_available_dataset import ResourceListAvailableDataset

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListAvailableDataset from a JSON string
resource_list_available_dataset_instance = ResourceListAvailableDataset.from_json(json)
# print the JSON string representation of the object
print(ResourceListAvailableDataset.to_json())

# convert the object into a dict
resource_list_available_dataset_dict = resource_list_available_dataset_instance.to_dict()
# create an instance of ResourceListAvailableDataset from a dict
resource_list_available_dataset_from_dict = ResourceListAvailableDataset.from_dict(resource_list_available_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


