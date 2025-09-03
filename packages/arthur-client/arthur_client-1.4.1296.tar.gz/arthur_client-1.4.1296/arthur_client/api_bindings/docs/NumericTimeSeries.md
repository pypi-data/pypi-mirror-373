# NumericTimeSeries


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dimensions** | [**List[Dimension]**](Dimension.md) | List of dimensions for the series. If multiple dimensions are uploaded with the same key, the one that is kept is undefined. | 
**values** | [**List[NumericPoint]**](NumericPoint.md) | List of numeric time series points. | 

## Example

```python
from arthur_client.api_bindings.models.numeric_time_series import NumericTimeSeries

# TODO update the JSON string below
json = "{}"
# create an instance of NumericTimeSeries from a JSON string
numeric_time_series_instance = NumericTimeSeries.from_json(json)
# print the JSON string representation of the object
print(NumericTimeSeries.to_json())

# convert the object into a dict
numeric_time_series_dict = numeric_time_series_instance.to_dict()
# create an instance of NumericTimeSeries from a dict
numeric_time_series_from_dict = NumericTimeSeries.from_dict(numeric_time_series_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


