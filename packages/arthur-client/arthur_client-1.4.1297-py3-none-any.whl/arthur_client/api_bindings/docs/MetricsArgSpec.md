# MetricsArgSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**arg_key** | **str** | Name of the argument. | 
**arg_value** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.metrics_arg_spec import MetricsArgSpec

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsArgSpec from a JSON string
metrics_arg_spec_instance = MetricsArgSpec.from_json(json)
# print the JSON string representation of the object
print(MetricsArgSpec.to_json())

# convert the object into a dict
metrics_arg_spec_dict = metrics_arg_spec_instance.to_dict()
# create an instance of MetricsArgSpec from a dict
metrics_arg_spec_from_dict = MetricsArgSpec.from_dict(metrics_arg_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


