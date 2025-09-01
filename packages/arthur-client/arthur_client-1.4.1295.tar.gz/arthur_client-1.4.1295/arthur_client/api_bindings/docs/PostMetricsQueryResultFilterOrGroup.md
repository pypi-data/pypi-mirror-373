# PostMetricsQueryResultFilterOrGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_or** | [**List[PostMetricsQueryResultFilterOrGroupOrInner]**](PostMetricsQueryResultFilterOrGroupOrInner.md) | List of filters to apply with OR operator. Needs to be provided if &#x60;and&#x60; is empty. | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_result_filter_or_group import PostMetricsQueryResultFilterOrGroup

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryResultFilterOrGroup from a JSON string
post_metrics_query_result_filter_or_group_instance = PostMetricsQueryResultFilterOrGroup.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryResultFilterOrGroup.to_json())

# convert the object into a dict
post_metrics_query_result_filter_or_group_dict = post_metrics_query_result_filter_or_group_instance.to_dict()
# create an instance of PostMetricsQueryResultFilterOrGroup from a dict
post_metrics_query_result_filter_or_group_from_dict = PostMetricsQueryResultFilterOrGroup.from_dict(post_metrics_query_result_filter_or_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


