# ValidationResult

Generic class to indicate a single validation and its outcome.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**validation_description** | **str** | Description of validation requirement. | 
**validation_outcome** | [**ValidationOutcome**](ValidationOutcome.md) | Outcome of the validation requirement. | 

## Example

```python
from arthur_client.api_bindings.models.validation_result import ValidationResult

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationResult from a JSON string
validation_result_instance = ValidationResult.from_json(json)
# print the JSON string representation of the object
print(ValidationResult.to_json())

# convert the object into a dict
validation_result_dict = validation_result_instance.to_dict()
# create an instance of ValidationResult from a dict
validation_result_from_dict = ValidationResult.from_dict(validation_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


