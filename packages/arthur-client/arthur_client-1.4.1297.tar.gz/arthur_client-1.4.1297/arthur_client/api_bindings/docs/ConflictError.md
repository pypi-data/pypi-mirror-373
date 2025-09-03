# ConflictError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | [optional] [default to 'Conflict']

## Example

```python
from arthur_client.api_bindings.models.conflict_error import ConflictError

# TODO update the JSON string below
json = "{}"
# create an instance of ConflictError from a JSON string
conflict_error_instance = ConflictError.from_json(json)
# print the JSON string representation of the object
print(ConflictError.to_json())

# convert the object into a dict
conflict_error_dict = conflict_error_instance.to_dict()
# create an instance of ConflictError from a dict
conflict_error_from_dict = ConflictError.from_dict(conflict_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


