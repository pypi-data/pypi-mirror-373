# SketchTimeSeries


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dimensions** | [**List[Dimension]**](Dimension.md) | List of dimensions for the series. If multiple dimensions are uploaded with the same key, the one that is kept is undefined. | 
**values** | [**List[SketchPoint]**](SketchPoint.md) | List of sketch-based time series points. | 

## Example

```python
from arthur_client.api_bindings.models.sketch_time_series import SketchTimeSeries

# TODO update the JSON string below
json = "{}"
# create an instance of SketchTimeSeries from a JSON string
sketch_time_series_instance = SketchTimeSeries.from_json(json)
# print the JSON string representation of the object
print(SketchTimeSeries.to_json())

# convert the object into a dict
sketch_time_series_dict = sketch_time_series_instance.to_dict()
# create an instance of SketchTimeSeries from a dict
sketch_time_series_from_dict = SketchTimeSeries.from_dict(sketch_time_series_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


