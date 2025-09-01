# PutModelMetricsSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cron** | **str** | Cron expression defining a cadence to run the model&#39;s metrics job on. Must specify a period greater than or equal to 5 minutes. | 
**lookback_period_seconds** | **int** | Lookback period of the scheduled job. | 
**name** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.put_model_metrics_schedule import PutModelMetricsSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of PutModelMetricsSchedule from a JSON string
put_model_metrics_schedule_instance = PutModelMetricsSchedule.from_json(json)
# print the JSON string representation of the object
print(PutModelMetricsSchedule.to_json())

# convert the object into a dict
put_model_metrics_schedule_dict = put_model_metrics_schedule_instance.to_dict()
# create an instance of PutModelMetricsSchedule from a dict
put_model_metrics_schedule_from_dict = PutModelMetricsSchedule.from_dict(put_model_metrics_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


