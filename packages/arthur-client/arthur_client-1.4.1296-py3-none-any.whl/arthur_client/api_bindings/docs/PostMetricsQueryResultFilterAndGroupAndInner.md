# PostMetricsQueryResultFilterAndGroupAndInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_and** | [**List[PostMetricsQueryResultFilterAndGroupAndInner]**](PostMetricsQueryResultFilterAndGroupAndInner.md) | List of filters to apply with AND operator. Needs to be provided if &#x60;or&#x60; is empty. | 
**var_or** | [**List[PostMetricsQueryResultFilterOrGroupOrInner]**](PostMetricsQueryResultFilterOrGroupOrInner.md) | List of filters to apply with OR operator. Needs to be provided if &#x60;and&#x60; is empty. | 
**column** | **str** | Column name to use for filtering metrics. | 
**op** | [**MetricsResultFilterOp**](MetricsResultFilterOp.md) | Operation to filter metrics. One of &#39;greater_than&#39;, &#39;less_than&#39;, &#39;equals&#39;, &#39;not_equals&#39;, &#39;greater_than_or_equal&#39;, &#39;less_than_or_equal&#39;, &#39;in&#39;, &#39;not_in&#39;. | 
**value** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_result_filter_and_group_and_inner import PostMetricsQueryResultFilterAndGroupAndInner

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryResultFilterAndGroupAndInner from a JSON string
post_metrics_query_result_filter_and_group_and_inner_instance = PostMetricsQueryResultFilterAndGroupAndInner.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryResultFilterAndGroupAndInner.to_json())

# convert the object into a dict
post_metrics_query_result_filter_and_group_and_inner_dict = post_metrics_query_result_filter_and_group_and_inner_instance.to_dict()
# create an instance of PostMetricsQueryResultFilterAndGroupAndInner from a dict
post_metrics_query_result_filter_and_group_and_inner_from_dict = PostMetricsQueryResultFilterAndGroupAndInner.from_dict(post_metrics_query_result_filter_and_group_and_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


