# BoundResource


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the bound resource. | 
**name** | **str** | Name of the bound resource. | 
**metadata** | [**ProjectBoundResourceMetadata**](ProjectBoundResourceMetadata.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.bound_resource import BoundResource

# TODO update the JSON string below
json = "{}"
# create an instance of BoundResource from a JSON string
bound_resource_instance = BoundResource.from_json(json)
# print the JSON string representation of the object
print(BoundResource.to_json())

# convert the object into a dict
bound_resource_dict = bound_resource_instance.to_dict()
# create an instance of BoundResource from a dict
bound_resource_from_dict = BoundResource.from_dict(bound_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


