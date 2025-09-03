# MetricsCalculationJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'metrics_calculation']
**scope_model_id** | **str** | The id of the model to calculate metrics. | 
**start_timestamp** | **datetime** | The start timestamp to use for fetching data. | 
**end_timestamp** | **datetime** | The end timestamp to use for fetching data. | 

## Example

```python
from arthur_client.api_bindings.models.metrics_calculation_job_spec import MetricsCalculationJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsCalculationJobSpec from a JSON string
metrics_calculation_job_spec_instance = MetricsCalculationJobSpec.from_json(json)
# print the JSON string representation of the object
print(MetricsCalculationJobSpec.to_json())

# convert the object into a dict
metrics_calculation_job_spec_dict = metrics_calculation_job_spec_instance.to_dict()
# create an instance of MetricsCalculationJobSpec from a dict
metrics_calculation_job_spec_from_dict = MetricsCalculationJobSpec.from_dict(metrics_calculation_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


