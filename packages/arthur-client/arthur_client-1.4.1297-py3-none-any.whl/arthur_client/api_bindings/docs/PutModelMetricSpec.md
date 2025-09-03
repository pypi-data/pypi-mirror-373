# PutModelMetricSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aggregation_specs** | [**List[AggregationSpec]**](AggregationSpec.md) | List of aggregations configured for the metric spec. | 

## Example

```python
from arthur_client.api_bindings.models.put_model_metric_spec import PutModelMetricSpec

# TODO update the JSON string below
json = "{}"
# create an instance of PutModelMetricSpec from a JSON string
put_model_metric_spec_instance = PutModelMetricSpec.from_json(json)
# print the JSON string representation of the object
print(PutModelMetricSpec.to_json())

# convert the object into a dict
put_model_metric_spec_dict = put_model_metric_spec_instance.to_dict()
# create an instance of PutModelMetricSpec from a dict
put_model_metric_spec_from_dict = PutModelMetricSpec.from_dict(put_model_metric_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


