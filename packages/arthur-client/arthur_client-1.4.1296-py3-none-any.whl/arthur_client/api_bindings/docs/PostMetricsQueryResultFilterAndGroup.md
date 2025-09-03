# PostMetricsQueryResultFilterAndGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_and** | [**List[PostMetricsQueryResultFilterAndGroupAndInner]**](PostMetricsQueryResultFilterAndGroupAndInner.md) | List of filters to apply with AND operator. Needs to be provided if &#x60;or&#x60; is empty. | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_query_result_filter_and_group import PostMetricsQueryResultFilterAndGroup

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsQueryResultFilterAndGroup from a JSON string
post_metrics_query_result_filter_and_group_instance = PostMetricsQueryResultFilterAndGroup.from_json(json)
# print the JSON string representation of the object
print(PostMetricsQueryResultFilterAndGroup.to_json())

# convert the object into a dict
post_metrics_query_result_filter_and_group_dict = post_metrics_query_result_filter_and_group_instance.to_dict()
# create an instance of PostMetricsQueryResultFilterAndGroup from a dict
post_metrics_query_result_filter_and_group_from_dict = PostMetricsQueryResultFilterAndGroup.from_dict(post_metrics_query_result_filter_and_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


