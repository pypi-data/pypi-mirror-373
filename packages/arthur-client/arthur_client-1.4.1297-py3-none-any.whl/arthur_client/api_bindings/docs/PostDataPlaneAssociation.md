# PostDataPlaneAssociation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_plane_id** | **str** | ID of the data plane. | 
**project_id** | **str** | ID of the project. | 

## Example

```python
from arthur_client.api_bindings.models.post_data_plane_association import PostDataPlaneAssociation

# TODO update the JSON string below
json = "{}"
# create an instance of PostDataPlaneAssociation from a JSON string
post_data_plane_association_instance = PostDataPlaneAssociation.from_json(json)
# print the JSON string representation of the object
print(PostDataPlaneAssociation.to_json())

# convert the object into a dict
post_data_plane_association_dict = post_data_plane_association_instance.to_dict()
# create an instance of PostDataPlaneAssociation from a dict
post_data_plane_association_from_dict = PostDataPlaneAssociation.from_dict(post_data_plane_association_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


