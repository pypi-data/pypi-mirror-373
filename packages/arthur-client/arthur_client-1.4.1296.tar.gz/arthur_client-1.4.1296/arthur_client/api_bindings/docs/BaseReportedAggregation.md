# BaseReportedAggregation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_name** | **str** | Name of the reported aggregation metric. | 
**description** | **str** | Description of the reported aggregation metric and what it aggregates. | 

## Example

```python
from arthur_client.api_bindings.models.base_reported_aggregation import BaseReportedAggregation

# TODO update the JSON string below
json = "{}"
# create an instance of BaseReportedAggregation from a JSON string
base_reported_aggregation_instance = BaseReportedAggregation.from_json(json)
# print the JSON string representation of the object
print(BaseReportedAggregation.to_json())

# convert the object into a dict
base_reported_aggregation_dict = base_reported_aggregation_instance.to_dict()
# create an instance of BaseReportedAggregation from a dict
base_reported_aggregation_from_dict = BaseReportedAggregation.from_dict(base_reported_aggregation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


