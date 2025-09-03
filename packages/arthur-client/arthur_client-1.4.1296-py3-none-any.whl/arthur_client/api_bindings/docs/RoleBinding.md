# RoleBinding


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the role binding. | 
**role** | [**BoundRole**](BoundRole.md) | Bound role. | 
**bound_resource_kind** | [**BoundResourceKind**](BoundResourceKind.md) | Kind of the bound resource. | 
**bound_resource** | [**BoundResource**](BoundResource.md) | Bound resource. | 
**bound_member_kind** | [**BoundMemberKind**](BoundMemberKind.md) | Kind of the bound member. | 
**bound_member** | [**BoundMember**](BoundMember.md) | Bound member. | 

## Example

```python
from arthur_client.api_bindings.models.role_binding import RoleBinding

# TODO update the JSON string below
json = "{}"
# create an instance of RoleBinding from a JSON string
role_binding_instance = RoleBinding.from_json(json)
# print the JSON string representation of the object
print(RoleBinding.to_json())

# convert the object into a dict
role_binding_dict = role_binding_instance.to_dict()
# create an instance of RoleBinding from a dict
role_binding_from_dict = RoleBinding.from_dict(role_binding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


