# SketchMetric


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the metric. | 
**sketch_series** | [**List[SketchTimeSeries]**](SketchTimeSeries.md) | List of sketch-based time series to upload for the metric. | 

## Example

```python
from arthur_client.api_bindings.models.sketch_metric import SketchMetric

# TODO update the JSON string below
json = "{}"
# create an instance of SketchMetric from a JSON string
sketch_metric_instance = SketchMetric.from_json(json)
# print the JSON string representation of the object
print(SketchMetric.to_json())

# convert the object into a dict
sketch_metric_dict = sketch_metric_instance.to_dict()
# create an instance of SketchMetric from a dict
sketch_metric_from_dict = SketchMetric.from_dict(sketch_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


