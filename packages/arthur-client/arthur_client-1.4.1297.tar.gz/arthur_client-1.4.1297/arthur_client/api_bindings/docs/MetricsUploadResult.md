# MetricsUploadResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_metrics** | **int** | Total number of metrics uploaded. | 
**num_counter_metrics** | **int** | Number of counter type metrics uploaded. | 
**num_sketch_metrics** | **int** | Number of sketch type metrics uploaded. | 
**num_series** | **int** | Number of series uploaded. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_upload_result import MetricsUploadResult

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsUploadResult from a JSON string
metrics_upload_result_instance = MetricsUploadResult.from_json(json)
# print the JSON string representation of the object
print(MetricsUploadResult.to_json())

# convert the object into a dict
metrics_upload_result_dict = metrics_upload_result_instance.to_dict()
# create an instance of MetricsUploadResult from a dict
metrics_upload_result_from_dict = MetricsUploadResult.from_dict(metrics_upload_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


