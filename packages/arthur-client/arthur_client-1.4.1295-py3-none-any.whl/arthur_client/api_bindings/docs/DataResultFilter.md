# DataResultFilter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**field_name** | **str** | Field name to use for filtering data. | 
**op** | [**DataResultFilterOp**](DataResultFilterOp.md) | Operation to filter data. One of &#39;greater_than&#39;, &#39;less_than&#39;, &#39;equals&#39;, &#39;not_equals&#39;, &#39;greater_than_or_equal&#39;, &#39;less_than_or_equal&#39;, &#39;in&#39;, &#39;not_in&#39;. | 
**value** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.data_result_filter import DataResultFilter

# TODO update the JSON string below
json = "{}"
# create an instance of DataResultFilter from a JSON string
data_result_filter_instance = DataResultFilter.from_json(json)
# print the JSON string representation of the object
print(DataResultFilter.to_json())

# convert the object into a dict
data_result_filter_dict = data_result_filter_instance.to_dict()
# create an instance of DataResultFilter from a dict
data_result_filter_from_dict = DataResultFilter.from_dict(data_result_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


