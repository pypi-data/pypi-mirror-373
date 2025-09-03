# SketchPoint


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **datetime** | Timestamp with timezone. Should be the timestamp of the start of the interval covered by &#39;value&#39;. | 
**value** | **str** | Base64-encoded string representation of a sketch. | 

## Example

```python
from arthur_client.api_bindings.models.sketch_point import SketchPoint

# TODO update the JSON string below
json = "{}"
# create an instance of SketchPoint from a JSON string
sketch_point_instance = SketchPoint.from_json(json)
# print the JSON string representation of the object
print(SketchPoint.to_json())

# convert the object into a dict
sketch_point_dict = sketch_point_instance.to_dict()
# create an instance of SketchPoint from a dict
sketch_point_from_dict = SketchPoint.from_dict(sketch_point_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


