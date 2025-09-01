# ModelMetricSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aggregation_specs** | [**List[AggregationSpec]**](AggregationSpec.md) | List of aggregations configured for the metric spec. | 
**id** | **str** | Unique ID of the metric spec. | 

## Example

```python
from arthur_client.api_bindings.models.model_metric_spec import ModelMetricSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ModelMetricSpec from a JSON string
model_metric_spec_instance = ModelMetricSpec.from_json(json)
# print the JSON string representation of the object
print(ModelMetricSpec.to_json())

# convert the object into a dict
model_metric_spec_dict = model_metric_spec_instance.to_dict()
# create an instance of ModelMetricSpec from a dict
model_metric_spec_from_dict = ModelMetricSpec.from_dict(model_metric_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


