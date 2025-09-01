# PostMetricsQueryResultFilterOrGroupOrInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_or** | [**List[PostMetricsQueryResultFilterOrGroupOrInner]**](PostMetricsQueryResultFilterOrGroupOrInner.md) | List of filters to apply with OR operator. Needs to be provided if &#x60;and&#x60; is empty. | 
**var_and** | [**List[PostMetricsQueryResultFilterAndGroupAndInner]**](PostMetricsQueryResultFilterAndGroupAndInner.md) | List of filters to apply with AND operator. Needs to be provided if &#x60;or&#x60; is empty. | 
**column** | **str** | Column name to use for filtering metrics. | 
**op** | [**MetricsResultFilterOp**](MetricsResultFilterOp.md) | Operation to filter metrics. One of &#39;greater_than&#39;, &#39;less_than&#39;, &#39;equals&#39;, &#39;not_equals&#39;, &#39;greater_than_or_equal&#39;, &#39;less_than_or_equal&#39;, &#39;in&#39;, &#39;not_in&#39;. | 
**value** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_result_filter_or_group_or_inner import PostMetricsQueryResultFilterOrGroupOrInner

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryResultFilterOrGroupOrInner from a JSON string
post_metrics_query_result_filter_or_group_or_inner_instance = PostMetricsQueryResultFilterOrGroupOrInner.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryResultFilterOrGroupOrInner.to_json())

# convert the object into a dict
post_metrics_query_result_filter_or_group_or_inner_dict = post_metrics_query_result_filter_or_group_or_inner_instance.to_dict()
# create an instance of PostMetricsQueryResultFilterOrGroupOrInner from a dict
post_metrics_query_result_filter_or_group_or_inner_from_dict = PostMetricsQueryResultFilterOrGroupOrInner.from_dict(post_metrics_query_result_filter_or_group_or_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


