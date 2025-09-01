# BoundRole


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the bound role. | 
**name** | **str** | Name of the role. | 

## Example

```python
from arthur_client.api_bindings.models.bound_role import BoundRole

# TODO update the JSON string below
json = "{}"
# create an instance of BoundRole from a JSON string
bound_role_instance = BoundRole.from_json(json)
# print the JSON string representation of the object
print(BoundRole.to_json())

# convert the object into a dict
bound_role_dict = bound_role_instance.to_dict()
# create an instance of BoundRole from a dict
bound_role_from_dict = BoundRole.from_dict(bound_role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


