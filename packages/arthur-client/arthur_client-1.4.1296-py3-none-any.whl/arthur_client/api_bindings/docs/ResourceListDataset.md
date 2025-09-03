# ResourceListDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Dataset]**](Dataset.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_dataset import ResourceListDataset

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListDataset from a JSON string
resource_list_dataset_instance = ResourceListDataset.from_json(json)
# print the JSON string representation of the object
print(ResourceListDataset.to_json())

# convert the object into a dict
resource_list_dataset_dict = resource_list_dataset_instance.to_dict()
# create an instance of ResourceListDataset from a dict
resource_list_dataset_from_dict = ResourceListDataset.from_dict(resource_list_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


