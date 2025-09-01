# ResourceListGroupMembership


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[GroupMembership]**](GroupMembership.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_group_membership import ResourceListGroupMembership

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListGroupMembership from a JSON string
resource_list_group_membership_instance = ResourceListGroupMembership.from_json(json)
# print the JSON string representation of the object
print(ResourceListGroupMembership.to_json())

# convert the object into a dict
resource_list_group_membership_dict = resource_list_group_membership_instance.to_dict()
# create an instance of ResourceListGroupMembership from a dict
resource_list_group_membership_from_dict = ResourceListGroupMembership.from_dict(resource_list_group_membership_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


