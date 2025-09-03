# NumericMetric


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the metric. | 
**numeric_series** | [**List[NumericTimeSeries]**](NumericTimeSeries.md) | List of numeric time series to upload for the metric. | 

## Example

```python
from arthur_client.api_bindings.models.numeric_metric import NumericMetric

# TODO update the JSON string below
json = "{}"
# create an instance of NumericMetric from a JSON string
numeric_metric_instance = NumericMetric.from_json(json)
# print the JSON string representation of the object
print(NumericMetric.to_json())

# convert the object into a dict
numeric_metric_dict = numeric_metric_instance.to_dict()
# create an instance of NumericMetric from a dict
numeric_metric_from_dict = NumericMetric.from_dict(numeric_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


