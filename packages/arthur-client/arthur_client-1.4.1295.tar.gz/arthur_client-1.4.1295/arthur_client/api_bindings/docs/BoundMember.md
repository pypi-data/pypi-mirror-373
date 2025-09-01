# BoundMember


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Id of the bound member. | 
**name** | **str** | Name of the bound member. | 

## Example

```python
from arthur_client.api_bindings.models.bound_member import BoundMember

# TODO update the JSON string below
json = "{}"
# create an instance of BoundMember from a JSON string
bound_member_instance = BoundMember.from_json(json)
# print the JSON string representation of the object
print(BoundMember.to_json())

# convert the object into a dict
bound_member_dict = bound_member_instance.to_dict()
# create an instance of BoundMember from a dict
bound_member_from_dict = BoundMember.from_dict(bound_member_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


