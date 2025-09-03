# ResourceListCustomAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[CustomAggregationSpecSchema]**](CustomAggregationSpecSchema.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_custom_aggregation_spec_schema import ResourceListCustomAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListCustomAggregationSpecSchema from a JSON string
resource_list_custom_aggregation_spec_schema_instance = ResourceListCustomAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(ResourceListCustomAggregationSpecSchema.to_json())

# convert the object into a dict
resource_list_custom_aggregation_spec_schema_dict = resource_list_custom_aggregation_spec_schema_instance.to_dict()
# create an instance of ResourceListCustomAggregationSpecSchema from a dict
resource_list_custom_aggregation_spec_schema_from_dict = ResourceListCustomAggregationSpecSchema.from_dict(resource_list_custom_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


