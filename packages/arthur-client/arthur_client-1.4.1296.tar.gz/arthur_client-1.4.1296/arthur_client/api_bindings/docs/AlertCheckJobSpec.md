# AlertCheckJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'alert_check']
**scope_model_id** | **str** | The id of the model to check alerts. | 
**check_range_start_timestamp** | **datetime** | The start timestamp to use for checking the alerts on the data. | 
**check_range_end_timestamp** | **datetime** | The end timestamp to use for checking the alerts on the data. | 

## Example

```python
from arthur_client.api_bindings.models.alert_check_job_spec import AlertCheckJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of AlertCheckJobSpec from a JSON string
alert_check_job_spec_instance = AlertCheckJobSpec.from_json(json)
# print the JSON string representation of the object
print(AlertCheckJobSpec.to_json())

# convert the object into a dict
alert_check_job_spec_dict = alert_check_job_spec_instance.to_dict()
# create an instance of AlertCheckJobSpec from a dict
alert_check_job_spec_from_dict = AlertCheckJobSpec.from_dict(alert_check_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


