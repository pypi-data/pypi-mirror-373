# MetricsUploadMetricsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the metric. | 
**numeric_series** | [**List[NumericTimeSeries]**](NumericTimeSeries.md) | List of numeric time series to upload for the metric. | 
**sketch_series** | [**List[SketchTimeSeries]**](SketchTimeSeries.md) | List of sketch-based time series to upload for the metric. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_upload_metrics_inner import MetricsUploadMetricsInner

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsUploadMetricsInner from a JSON string
metrics_upload_metrics_inner_instance = MetricsUploadMetricsInner.from_json(json)
# print the JSON string representation of the object
print(MetricsUploadMetricsInner.to_json())

# convert the object into a dict
metrics_upload_metrics_inner_dict = metrics_upload_metrics_inner_instance.to_dict()
# create an instance of MetricsUploadMetricsInner from a dict
metrics_upload_metrics_inner_from_dict = MetricsUploadMetricsInner.from_dict(metrics_upload_metrics_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


