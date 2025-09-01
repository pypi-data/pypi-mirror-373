# DataPlaneAssociation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the data plane association. | 
**data_plane_id** | **str** | ID of the data plane. | 
**project_id** | **str** | ID of the project. | 
**data_plane** | [**DataPlane**](DataPlane.md) |  | [optional] 
**project** | [**Project**](Project.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.data_plane_association import DataPlaneAssociation

# TODO update the JSON string below
json = "{}"
# create an instance of DataPlaneAssociation from a JSON string
data_plane_association_instance = DataPlaneAssociation.from_json(json)
# print the JSON string representation of the object
print(DataPlaneAssociation.to_json())

# convert the object into a dict
data_plane_association_dict = data_plane_association_instance.to_dict()
# create an instance of DataPlaneAssociation from a dict
data_plane_association_from_dict = DataPlaneAssociation.from_dict(data_plane_association_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


