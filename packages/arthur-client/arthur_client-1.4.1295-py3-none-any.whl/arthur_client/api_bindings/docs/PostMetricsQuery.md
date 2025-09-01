# PostMetricsQuery


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **str** | Query for retrieving the metrics. | 
**time_range** | [**PostMetricsQueryTimeRange**](PostMetricsQueryTimeRange.md) | Time range to filter the metrics by. | 
**interval** | [**AlertRuleInterval**](AlertRuleInterval.md) |  | [optional] 
**limit** | **int** | Limit the number of metrics returned. Defaults to 50. | [optional] [default to 50]
**result_filter** | [**ResultFilter**](ResultFilter.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query import PostMetricsQuery

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQuery from a JSON string
post_metrics_query_instance = PostMetricsQuery.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQuery.to_json())

# convert the object into a dict
post_metrics_query_dict = post_metrics_query_instance.to_dict()
# create an instance of PostMetricsQuery from a dict
post_metrics_query_from_dict = PostMetricsQuery.from_dict(post_metrics_query_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


