# ResourceListDataPlaneAssociation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[DataPlaneAssociation]**](DataPlaneAssociation.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_data_plane_association import ResourceListDataPlaneAssociation

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListDataPlaneAssociation from a JSON string
resource_list_data_plane_association_instance = ResourceListDataPlaneAssociation.from_json(json)
# print the JSON string representation of the object
print(ResourceListDataPlaneAssociation.to_json())

# convert the object into a dict
resource_list_data_plane_association_dict = resource_list_data_plane_association_instance.to_dict()
# create an instance of ResourceListDataPlaneAssociation from a dict
resource_list_data_plane_association_from_dict = ResourceListDataPlaneAssociation.from_dict(resource_list_data_plane_association_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


