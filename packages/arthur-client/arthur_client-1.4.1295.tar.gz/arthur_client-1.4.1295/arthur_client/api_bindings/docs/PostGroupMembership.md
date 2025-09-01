# PostGroupMembership


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_ids** | **List[str]** | The ID of the user to add to the group. | 

## Example

```python
from arthur_client.api_bindings.models.post_group_membership import PostGroupMembership

# TODO update the JSON string below
json = "{}"
# create an instance of PostGroupMembership from a JSON string
post_group_membership_instance = PostGroupMembership.from_json(json)
# print the JSON string representation of the object
print(PostGroupMembership.to_json())

# convert the object into a dict
post_group_membership_dict = post_group_membership_instance.to_dict()
# create an instance of PostGroupMembership from a dict
post_group_membership_from_dict = PostGroupMembership.from_dict(post_group_membership_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


