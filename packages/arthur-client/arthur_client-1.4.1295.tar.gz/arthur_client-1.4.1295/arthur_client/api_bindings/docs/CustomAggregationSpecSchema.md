# CustomAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier of the custom aggregation with version. | 
**name** | **str** | Name of the custom aggregation function. | 
**description** | **str** |  | [optional] 
**workspace_id** | **str** | Unique identifier of the custom aggregation&#39;s parent workspace. | 
**versions** | [**List[CustomAggregationVersionSpecSchema]**](CustomAggregationVersionSpecSchema.md) | List of versions of the custom aggregation configuration. | 
**latest_version** | **int** | Max/latest version of the custom aggregation that exists. This version may or may not be included in the list of versions depending on applied filters. | 

## Example

```python
from arthur_client.api_bindings.models.custom_aggregation_spec_schema import CustomAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CustomAggregationSpecSchema from a JSON string
custom_aggregation_spec_schema_instance = CustomAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(CustomAggregationSpecSchema.to_json())

# convert the object into a dict
custom_aggregation_spec_schema_dict = custom_aggregation_spec_schema_instance.to_dict()
# create an instance of CustomAggregationSpecSchema from a dict
custom_aggregation_spec_schema_from_dict = CustomAggregationSpecSchema.from_dict(custom_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


