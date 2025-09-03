# PutCustomAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reported_aggregations** | [**List[ReportedCustomAggregation]**](ReportedCustomAggregation.md) | Metadata for every aggregation the custom aggregation reports. | 
**aggregate_args** | [**List[CustomAggregationVersionSpecSchemaAggregateArgsInner]**](CustomAggregationVersionSpecSchemaAggregateArgsInner.md) | List of parameters to the custom aggregation&#39;s query function. | 
**sql** | **str** | DuckDBSQL query for the custom aggregation. | 

## Example

```python
from arthur_client.api_bindings.models.put_custom_aggregation_spec_schema import PutCustomAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PutCustomAggregationSpecSchema from a JSON string
put_custom_aggregation_spec_schema_instance = PutCustomAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(PutCustomAggregationSpecSchema.to_json())

# convert the object into a dict
put_custom_aggregation_spec_schema_dict = put_custom_aggregation_spec_schema_instance.to_dict()
# create an instance of PutCustomAggregationSpecSchema from a dict
put_custom_aggregation_spec_schema_from_dict = PutCustomAggregationSpecSchema.from_dict(put_custom_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


