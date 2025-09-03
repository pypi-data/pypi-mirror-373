# ResourceListDataPlane


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[DataPlane]**](DataPlane.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_data_plane import ResourceListDataPlane

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListDataPlane from a JSON string
resource_list_data_plane_instance = ResourceListDataPlane.from_json(json)
# print the JSON string representation of the object
print(ResourceListDataPlane.to_json())

# convert the object into a dict
resource_list_data_plane_dict = resource_list_data_plane_instance.to_dict()
# create an instance of ResourceListDataPlane from a dict
resource_list_data_plane_from_dict = ResourceListDataPlane.from_dict(resource_list_data_plane_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


