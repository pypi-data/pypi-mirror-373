# GenerateMetricsSpecRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_ids** | **List[str]** | List of dataset IDs for which to generate a model metrics spec. Datasets must be in the project in the path. | 

## Example

```python
from arthur_client.api_bindings.models.generate_metrics_spec_request import GenerateMetricsSpecRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GenerateMetricsSpecRequest from a JSON string
generate_metrics_spec_request_instance = GenerateMetricsSpecRequest.from_json(json)
# print the JSON string representation of the object
print(GenerateMetricsSpecRequest.to_json())

# convert the object into a dict
generate_metrics_spec_request_dict = generate_metrics_spec_request_instance.to_dict()
# create an instance of GenerateMetricsSpecRequest from a dict
generate_metrics_spec_request_from_dict = GenerateMetricsSpecRequest.from_dict(generate_metrics_spec_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


