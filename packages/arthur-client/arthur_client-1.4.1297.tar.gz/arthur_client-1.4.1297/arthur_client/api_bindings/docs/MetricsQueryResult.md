# MetricsQueryResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | **List[Optional[object]]** | Results of the metrics query. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_query_result import MetricsQueryResult

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsQueryResult from a JSON string
metrics_query_result_instance = MetricsQueryResult.from_json(json)
# print the JSON string representation of the object
print(MetricsQueryResult.to_json())

# convert the object into a dict
metrics_query_result_dict = metrics_query_result_instance.to_dict()
# create an instance of MetricsQueryResult from a dict
metrics_query_result_from_dict = MetricsQueryResult.from_dict(metrics_query_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


