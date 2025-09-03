# PostCustomAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reported_aggregations** | [**List[ReportedCustomAggregation]**](ReportedCustomAggregation.md) | Metadata for every aggregation the custom aggregation reports. | 
**aggregate_args** | [**List[CustomAggregationVersionSpecSchemaAggregateArgsInner]**](CustomAggregationVersionSpecSchemaAggregateArgsInner.md) | List of parameters to the custom aggregation&#39;s query function. | 
**sql** | **str** | DuckDBSQL query for the custom aggregation. | 
**name** | **str** | Name of the custom aggregation function. | 
**description** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_custom_aggregation_spec_schema import PostCustomAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomAggregationSpecSchema from a JSON string
post_custom_aggregation_spec_schema_instance = PostCustomAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(PostCustomAggregationSpecSchema.to_json())

# convert the object into a dict
post_custom_aggregation_spec_schema_dict = post_custom_aggregation_spec_schema_instance.to_dict()
# create an instance of PostCustomAggregationSpecSchema from a dict
post_custom_aggregation_spec_schema_from_dict = PostCustomAggregationSpecSchema.from_dict(post_custom_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


