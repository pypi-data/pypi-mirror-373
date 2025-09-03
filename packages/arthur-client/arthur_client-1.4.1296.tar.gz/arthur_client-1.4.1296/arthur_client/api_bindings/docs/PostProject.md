# PostProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the project. | 
**description** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_project import PostProject

# TODO update the JSON string below
json = "{}"
# create an instance of PostProject from a JSON string
post_project_instance = PostProject.from_json(json)
# print the JSON string representation of the object
print(PostProject.to_json())

# convert the object into a dict
post_project_dict = post_project_instance.to_dict()
# create an instance of PostProject from a dict
post_project_from_dict = PostProject.from_dict(post_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


