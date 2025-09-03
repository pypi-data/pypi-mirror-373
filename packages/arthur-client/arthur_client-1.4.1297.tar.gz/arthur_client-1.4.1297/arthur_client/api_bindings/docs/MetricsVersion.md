# MetricsVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**version_num** | **int** | Version id for the set of metrics for this model. | 
**scope_model_id** | **str** | Model id of the model for this metric version. | 
**range_start** | **datetime** | Start timestamp of the metrics range included in this metric version. | 
**range_end** | **datetime** | End timestamp of the metrics range included in this metric version. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_version import MetricsVersion

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsVersion from a JSON string
metrics_version_instance = MetricsVersion.from_json(json)
# print the JSON string representation of the object
print(MetricsVersion.to_json())

# convert the object into a dict
metrics_version_dict = metrics_version_instance.to_dict()
# create an instance of MetricsVersion from a dict
metrics_version_from_dict = MetricsVersion.from_dict(metrics_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


