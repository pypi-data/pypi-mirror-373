# PostMetricsQueryTimeRange


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start** | **datetime** | Start timestamp of the metrics range. | 
**end** | **datetime** | End timestamp of the metrics range. | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_time_range import PostMetricsQueryTimeRange

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryTimeRange from a JSON string
post_metrics_query_time_range_instance = PostMetricsQueryTimeRange.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryTimeRange.to_json())

# convert the object into a dict
post_metrics_query_time_range_dict = post_metrics_query_time_range_instance.to_dict()
# create an instance of PostMetricsQueryTimeRange from a dict
post_metrics_query_time_range_from_dict = PostMetricsQueryTimeRange.from_dict(post_metrics_query_time_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


