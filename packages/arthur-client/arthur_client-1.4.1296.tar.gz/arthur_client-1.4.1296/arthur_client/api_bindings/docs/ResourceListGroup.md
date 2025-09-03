# ResourceListGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Group]**](Group.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_group import ResourceListGroup

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListGroup from a JSON string
resource_list_group_instance = ResourceListGroup.from_json(json)
# print the JSON string representation of the object
print(ResourceListGroup.to_json())

# convert the object into a dict
resource_list_group_dict = resource_list_group_instance.to_dict()
# create an instance of ResourceListGroup from a dict
resource_list_group_from_dict = ResourceListGroup.from_dict(resource_list_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


