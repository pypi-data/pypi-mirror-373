# UpsolveToken


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** | JWT for use with Upsolve API. | 

## Example

```python
from arthur_client.api_bindings.models.upsolve_token import UpsolveToken

# TODO update the JSON string below
json = "{}"
# create an instance of UpsolveToken from a JSON string
upsolve_token_instance = UpsolveToken.from_json(json)
# print the JSON string representation of the object
print(UpsolveToken.to_json())

# convert the object into a dict
upsolve_token_dict = upsolve_token_instance.to_dict()
# create an instance of UpsolveToken from a dict
upsolve_token_from_dict = UpsolveToken.from_dict(upsolve_token_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


