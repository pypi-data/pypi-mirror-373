# ResultFilter

Filter to apply to the query results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column** | **str** | Column name to use for filtering metrics. | 
**op** | [**MetricsResultFilterOp**](MetricsResultFilterOp.md) | Operation to filter metrics. One of &#39;greater_than&#39;, &#39;less_than&#39;, &#39;equals&#39;, &#39;not_equals&#39;, &#39;greater_than_or_equal&#39;, &#39;less_than_or_equal&#39;, &#39;in&#39;, &#39;not_in&#39;. | 
**value** | **object** |  | 
**var_and** | [**List[PostMetricsQueryResultFilterAndGroupAndInner]**](PostMetricsQueryResultFilterAndGroupAndInner.md) | List of filters to apply with AND operator. Needs to be provided if &#x60;or&#x60; is empty. | 
**var_or** | [**List[PostMetricsQueryResultFilterOrGroupOrInner]**](PostMetricsQueryResultFilterOrGroupOrInner.md) | List of filters to apply with OR operator. Needs to be provided if &#x60;and&#x60; is empty. | 

## Example

```python
from arthur_client.api_bindings.models.result_filter import ResultFilter

# TODO update the JSON string below
json = "{}"
# create an instance of ResultFilter from a JSON string
result_filter_instance = ResultFilter.from_json(json)
# print the JSON string representation of the object
print(ResultFilter.to_json())

# convert the object into a dict
result_filter_dict = result_filter_instance.to_dict()
# create an instance of ResultFilter from a dict
result_filter_from_dict = ResultFilter.from_dict(result_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


