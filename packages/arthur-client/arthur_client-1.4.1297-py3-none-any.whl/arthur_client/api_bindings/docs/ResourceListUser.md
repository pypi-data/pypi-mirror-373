# ResourceListUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[User]**](User.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_user import ResourceListUser

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListUser from a JSON string
resource_list_user_instance = ResourceListUser.from_json(json)
# print the JSON string representation of the object
print(ResourceListUser.to_json())

# convert the object into a dict
resource_list_user_dict = resource_list_user_instance.to_dict()
# create an instance of ResourceListUser from a dict
resource_list_user_from_dict = ResourceListUser.from_dict(resource_list_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


