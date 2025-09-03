# ResourceListAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[AggregationSpecSchema]**](AggregationSpecSchema.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_aggregation_spec_schema import ResourceListAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListAggregationSpecSchema from a JSON string
resource_list_aggregation_spec_schema_instance = ResourceListAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(ResourceListAggregationSpecSchema.to_json())

# convert the object into a dict
resource_list_aggregation_spec_schema_dict = resource_list_aggregation_spec_schema_instance.to_dict()
# create an instance of ResourceListAggregationSpecSchema from a dict
resource_list_aggregation_spec_schema_from_dict = ResourceListAggregationSpecSchema.from_dict(resource_list_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


