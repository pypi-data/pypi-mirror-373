# Role


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the role. | 
**name** | **str** | Name of the role. | 
**description** | **str** |  | 
**organization_bindable** | **bool** | Whether the role can be bound to an organization. | 
**workspace_bindable** | **bool** | Whether the role can be bound to a workspace. | 
**project_bindable** | **bool** | Whether the role can be bound to a project. | 
**data_plane_bindable** | **bool** | Whether the role can be bound to a data plane. | 
**permissions** | [**List[PermissionName]**](PermissionName.md) | Permissions granted by the role. | 
**base_role_ids** | **List[str]** | List of IDs of the roles this role inherits permissions from, if any. | 

## Example

```python
from arthur_client.api_bindings.models.role import Role

# TODO update the JSON string below
json = "{}"
# create an instance of Role from a JSON string
role_instance = Role.from_json(json)
# print the JSON string representation of the object
print(Role.to_json())

# convert the object into a dict
role_dict = role_instance.to_dict()
# create an instance of Role from a dict
role_from_dict = Role.from_dict(role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


