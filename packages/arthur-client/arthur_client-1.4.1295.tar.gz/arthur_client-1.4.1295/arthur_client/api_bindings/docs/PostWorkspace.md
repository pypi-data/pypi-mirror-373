# PostWorkspace


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the workspace. | 

## Example

```python
from arthur_client.api_bindings.models.post_workspace import PostWorkspace

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkspace from a JSON string
post_workspace_instance = PostWorkspace.from_json(json)
# print the JSON string representation of the object
print(PostWorkspace.to_json())

# convert the object into a dict
post_workspace_dict = post_workspace_instance.to_dict()
# create an instance of PostWorkspace from a dict
post_workspace_from_dict = PostWorkspace.from_dict(post_workspace_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


