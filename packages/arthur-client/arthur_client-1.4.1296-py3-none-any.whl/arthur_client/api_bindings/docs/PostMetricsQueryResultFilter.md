# PostMetricsQueryResultFilter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column** | **str** | Column name to use for filtering metrics. | 
**op** | [**MetricsResultFilterOp**](MetricsResultFilterOp.md) | Operation to filter metrics. One of &#39;greater_than&#39;, &#39;less_than&#39;, &#39;equals&#39;, &#39;not_equals&#39;, &#39;greater_than_or_equal&#39;, &#39;less_than_or_equal&#39;, &#39;in&#39;, &#39;not_in&#39;. | 
**value** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_result_filter import PostMetricsQueryResultFilter

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryResultFilter from a JSON string
post_metrics_query_result_filter_instance = PostMetricsQueryResultFilter.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryResultFilter.to_json())

# convert the object into a dict
post_metrics_query_result_filter_dict = post_metrics_query_result_filter_instance.to_dict()
# create an instance of PostMetricsQueryResultFilter from a dict
post_metrics_query_result_filter_from_dict = PostMetricsQueryResultFilter.from_dict(post_metrics_query_result_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


