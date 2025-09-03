# PostGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the group. | 
**description** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_group import PostGroup

# TODO update the JSON string below
json = "{}"
# create an instance of PostGroup from a JSON string
post_group_instance = PostGroup.from_json(json)
# print the JSON string representation of the object
print(PostGroup.to_json())

# convert the object into a dict
post_group_dict = post_group_instance.to_dict()
# create an instance of PostGroup from a dict
post_group_from_dict = PostGroup.from_dict(post_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


