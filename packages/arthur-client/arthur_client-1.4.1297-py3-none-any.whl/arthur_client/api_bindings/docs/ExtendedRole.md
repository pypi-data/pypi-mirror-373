# ExtendedRole


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
**permissions** | [**List[Permission]**](Permission.md) | Permissions granted by the role. | 
**base_roles** | [**List[BaseRole]**](BaseRole.md) | List of IDs of the roles this role inherits permissions from, if any. | 

## Example

```python
from arthur_client.api_bindings.models.extended_role import ExtendedRole

# TODO update the JSON string below
json = "{}"
# create an instance of ExtendedRole from a JSON string
extended_role_instance = ExtendedRole.from_json(json)
# print the JSON string representation of the object
print(ExtendedRole.to_json())

# convert the object into a dict
extended_role_dict = extended_role_instance.to_dict()
# create an instance of ExtendedRole from a dict
extended_role_from_dict = ExtendedRole.from_dict(extended_role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


