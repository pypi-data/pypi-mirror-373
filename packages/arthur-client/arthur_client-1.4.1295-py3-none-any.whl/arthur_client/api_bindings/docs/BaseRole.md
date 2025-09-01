# BaseRole


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the role this role inherits permissions from. | 
**name** | **str** | Name of the role this role inherits permissions from. | 
**description** | **str** |  | 

## Example

```python
from arthur_client.api_bindings.models.base_role import BaseRole

# TODO update the JSON string below
json = "{}"
# create an instance of BaseRole from a JSON string
base_role_instance = BaseRole.from_json(json)
# print the JSON string representation of the object
print(BaseRole.to_json())

# convert the object into a dict
base_role_dict = base_role_instance.to_dict()
# create an instance of BaseRole from a dict
base_role_from_dict = BaseRole.from_dict(base_role_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


