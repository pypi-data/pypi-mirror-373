# ValidationResults

This class is a generic class for any endpoints returning multiple validation errors.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**validation_results** | [**List[ValidationResult]**](ValidationResult.md) |  | 

## Example

```python
from arthur_client.api_bindings.models.validation_results import ValidationResults

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationResults from a JSON string
validation_results_instance = ValidationResults.from_json(json)
# print the JSON string representation of the object
print(ValidationResults.to_json())

# convert the object into a dict
validation_results_dict = validation_results_instance.to_dict()
# create an instance of ValidationResults from a dict
validation_results_from_dict = ValidationResults.from_dict(validation_results_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


