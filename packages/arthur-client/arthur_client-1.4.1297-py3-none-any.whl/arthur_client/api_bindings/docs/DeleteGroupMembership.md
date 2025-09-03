# DeleteGroupMembership


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_ids** | **List[str]** | The ID of the user to remove from the group. | 

## Example

```python
from arthur_client.api_bindings.models.delete_group_membership import DeleteGroupMembership

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteGroupMembership from a JSON string
delete_group_membership_instance = DeleteGroupMembership.from_json(json)
# print the JSON string representation of the object
print(DeleteGroupMembership.to_json())

# convert the object into a dict
delete_group_membership_dict = delete_group_membership_instance.to_dict()
# create an instance of DeleteGroupMembership from a dict
delete_group_membership_from_dict = DeleteGroupMembership.from_dict(delete_group_membership_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


