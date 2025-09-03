# AggregationSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aggregation_id** | **str** | Unique identifier of the aggregation. | 
**aggregation_init_args** | [**List[MetricsArgSpec]**](MetricsArgSpec.md) | List of arguments to the aggregation&#39;s init function. | 
**aggregation_args** | [**List[MetricsArgSpec]**](MetricsArgSpec.md) | List of arguments to the aggregation&#39;s aggregate function. | 
**aggregation_kind** | [**AggregationKind**](AggregationKind.md) | Type of aggregation to use for the metric spec. | [optional] 
**aggregation_version** | **int** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.aggregation_spec import AggregationSpec

# TODO update the JSON string below
json = "{}"
# create an instance of AggregationSpec from a JSON string
aggregation_spec_instance = AggregationSpec.from_json(json)
# print the JSON string representation of the object
print(AggregationSpec.to_json())

# convert the object into a dict
aggregation_spec_dict = aggregation_spec_instance.to_dict()
# create an instance of AggregationSpec from a dict
aggregation_spec_from_dict = AggregationSpec.from_dict(aggregation_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


