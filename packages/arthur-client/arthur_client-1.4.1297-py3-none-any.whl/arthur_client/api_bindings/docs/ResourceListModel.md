# ResourceListModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Model]**](Model.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_model import ResourceListModel

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListModel from a JSON string
resource_list_model_instance = ResourceListModel.from_json(json)
# print the JSON string representation of the object
print(ResourceListModel.to_json())

# convert the object into a dict
resource_list_model_dict = resource_list_model_instance.to_dict()
# create an instance of ResourceListModel from a dict
resource_list_model_from_dict = ResourceListModel.from_dict(resource_list_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


