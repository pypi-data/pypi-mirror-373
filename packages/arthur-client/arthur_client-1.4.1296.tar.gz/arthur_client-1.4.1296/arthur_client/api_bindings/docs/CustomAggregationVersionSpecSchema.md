# CustomAggregationVersionSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_aggregation_id** | **str** | ID of parent custom aggregation. | 
**version** | **int** | Version number of the custom aggregation function. | 
**authored_by** | [**User**](User.md) |  | 
**created_at** | **datetime** | Time of aggregation creation. | 
**reported_aggregations** | [**List[ReportedCustomAggregation]**](ReportedCustomAggregation.md) | Metadata for every aggregation the custom aggregation reports. | 
**aggregate_args** | [**List[CustomAggregationVersionSpecSchemaAggregateArgsInner]**](CustomAggregationVersionSpecSchemaAggregateArgsInner.md) | List of parameters to the custom aggregation&#39;s query function. | 
**sql** | **str** | DuckDBSQL query for the custom aggregation. | 

## Example

```python
from arthur_client.api_bindings.models.custom_aggregation_version_spec_schema import CustomAggregationVersionSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CustomAggregationVersionSpecSchema from a JSON string
custom_aggregation_version_spec_schema_instance = CustomAggregationVersionSpecSchema.from_json(json)
# print the JSON string representation of the object
print(CustomAggregationVersionSpecSchema.to_json())

# convert the object into a dict
custom_aggregation_version_spec_schema_dict = custom_aggregation_version_spec_schema_instance.to_dict()
# create an instance of CustomAggregationVersionSpecSchema from a dict
custom_aggregation_version_spec_schema_from_dict = CustomAggregationVersionSpecSchema.from_dict(custom_aggregation_version_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


