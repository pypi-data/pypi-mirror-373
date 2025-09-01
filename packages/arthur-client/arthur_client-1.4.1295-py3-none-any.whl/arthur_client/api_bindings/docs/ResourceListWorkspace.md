# ResourceListWorkspace


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Workspace]**](Workspace.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_workspace import ResourceListWorkspace

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListWorkspace from a JSON string
resource_list_workspace_instance = ResourceListWorkspace.from_json(json)
# print the JSON string representation of the object
print(ResourceListWorkspace.to_json())

# convert the object into a dict
resource_list_workspace_dict = resource_list_workspace_instance.to_dict()
# create an instance of ResourceListWorkspace from a dict
resource_list_workspace_from_dict = ResourceListWorkspace.from_dict(resource_list_workspace_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


