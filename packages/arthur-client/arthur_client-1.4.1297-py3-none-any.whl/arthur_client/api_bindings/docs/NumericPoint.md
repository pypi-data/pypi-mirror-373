# NumericPoint


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **datetime** | Timestamp with timezone. Should be the timestamp of the start of the interval covered by &#39;value&#39;. | 
**value** | **float** | Floating point value for the metric. | 

## Example

```python
from arthur_client.api_bindings.models.numeric_point import NumericPoint

# TODO update the JSON string below
json = "{}"
# create an instance of NumericPoint from a JSON string
numeric_point_instance = NumericPoint.from_json(json)
# print the JSON string representation of the object
print(NumericPoint.to_json())

# convert the object into a dict
numeric_point_dict = numeric_point_instance.to_dict()
# create an instance of NumericPoint from a dict
numeric_point_from_dict = NumericPoint.from_dict(numeric_point_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


