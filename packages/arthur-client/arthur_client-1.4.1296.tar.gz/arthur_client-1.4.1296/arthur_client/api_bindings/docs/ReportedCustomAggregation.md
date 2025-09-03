# ReportedCustomAggregation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_name** | **str** | Name of the reported aggregation metric. | 
**description** | **str** | Description of the reported aggregation metric and what it aggregates. | 
**value_column** | **str** | Name of the column returned from the SQL query holding the metric value. | 
**timestamp_column** | **str** | Name of the column returned from the SQL query holding the timestamp buckets. | 
**metric_kind** | [**AggregationMetricType**](AggregationMetricType.md) | Return type of the reported aggregation metric value. | 
**dimension_columns** | **List[str]** | Name of any dimension columns returned from the SQL query. Max length is 1. | 

## Example

```python
from arthur_client.api_bindings.models.reported_custom_aggregation import ReportedCustomAggregation

# TODO update the JSON string below
json = "{}"
# create an instance of ReportedCustomAggregation from a JSON string
reported_custom_aggregation_instance = ReportedCustomAggregation.from_json(json)
# print the JSON string representation of the object
print(ReportedCustomAggregation.to_json())

# convert the object into a dict
reported_custom_aggregation_dict = reported_custom_aggregation_instance.to_dict()
# create an instance of ReportedCustomAggregation from a dict
reported_custom_aggregation_from_dict = ReportedCustomAggregation.from_dict(reported_custom_aggregation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


