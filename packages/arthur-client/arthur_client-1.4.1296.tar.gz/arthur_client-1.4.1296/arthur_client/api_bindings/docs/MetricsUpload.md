# MetricsUpload

The set of metrics that are available to submit via the PostMetrics API Notably, this does not include systems metrics jobs

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metrics** | [**List[MetricsUploadMetricsInner]**](MetricsUploadMetricsInner.md) | List of metrics to upload. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_upload import MetricsUpload

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsUpload from a JSON string
metrics_upload_instance = MetricsUpload.from_json(json)
# print the JSON string representation of the object
print(MetricsUpload.to_json())

# convert the object into a dict
metrics_upload_dict = metrics_upload_instance.to_dict()
# create an instance of MetricsUpload from a dict
metrics_upload_from_dict = MetricsUpload.from_dict(metrics_upload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


