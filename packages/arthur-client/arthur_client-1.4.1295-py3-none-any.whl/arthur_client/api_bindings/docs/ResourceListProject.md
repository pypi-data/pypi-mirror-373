# ResourceListProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Project]**](Project.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_project import ResourceListProject

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListProject from a JSON string
resource_list_project_instance = ResourceListProject.from_json(json)
# print the JSON string representation of the object
print(ResourceListProject.to_json())

# convert the object into a dict
resource_list_project_dict = resource_list_project_instance.to_dict()
# create an instance of ResourceListProject from a dict
resource_list_project_from_dict = ResourceListProject.from_dict(resource_list_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


