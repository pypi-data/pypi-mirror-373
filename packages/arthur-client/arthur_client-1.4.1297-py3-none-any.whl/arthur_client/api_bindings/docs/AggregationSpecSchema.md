# AggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the aggregation function. | 
**id** | **str** | Unique identifier of the aggregation function. | 
**description** | **str** | Description of the aggregation function and what it aggregates. | 
**metric_type** | [**AggregationMetricType**](AggregationMetricType.md) | Return type of the aggregations aggregate function. | 
**init_args** | [**List[AggregationSpecSchemaInitArgsInner]**](AggregationSpecSchemaInitArgsInner.md) | List of parameters to the aggregation&#39;s init function. | 
**aggregate_args** | [**List[AggregationSpecSchemaInitArgsInner]**](AggregationSpecSchemaInitArgsInner.md) | List of parameters to the aggregation&#39;s aggregate function. | 
**reported_aggregations** | [**List[BaseReportedAggregation]**](BaseReportedAggregation.md) | List of aggregations reported by the metric. | 

## Example

```python
from arthur_client.api_bindings.models.aggregation_spec_schema import AggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of AggregationSpecSchema from a JSON string
aggregation_spec_schema_instance = AggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(AggregationSpecSchema.to_json())

# convert the object into a dict
aggregation_spec_schema_dict = aggregation_spec_schema_instance.to_dict()
# create an instance of AggregationSpecSchema from a dict
aggregation_spec_schema_from_dict = AggregationSpecSchema.from_dict(aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


