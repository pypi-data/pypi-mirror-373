# ProjectBoundResourceMetadata


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workspace_id** | **str** | ID of the parent workspace. | 
**workspace_name** | **str** | Name of the parent workspace. | 

## Example

```python
from arthur_client.api_bindings.models.project_bound_resource_metadata import ProjectBoundResourceMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectBoundResourceMetadata from a JSON string
project_bound_resource_metadata_instance = ProjectBoundResourceMetadata.from_json(json)
# print the JSON string representation of the object
print(ProjectBoundResourceMetadata.to_json())

# convert the object into a dict
project_bound_resource_metadata_dict = project_bound_resource_metadata_instance.to_dict()
# create an instance of ProjectBoundResourceMetadata from a dict
project_bound_resource_metadata_from_dict = ProjectBoundResourceMetadata.from_dict(project_bound_resource_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


