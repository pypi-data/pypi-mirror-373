# FetchDataJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'fetch_data']
**dataset_id** | **str** |  | [optional] 
**available_dataset_id** | **str** |  | [optional] 
**start_timestamp** | **datetime** | The start timestamp to use for fetching data. | 
**end_timestamp** | **datetime** | The end timestamp to use for fetching data. | 
**operation_id** | **str** | The id of the data retrieval operation. | 
**data_filters** | [**List[DataResultFilter]**](DataResultFilter.md) | Filters to apply to the metrics data. | 
**pagination_options** | [**ConnectorPaginationOptions**](ConnectorPaginationOptions.md) | Pagination options to use for fetching data. | 

## Example

```python
from arthur_client.api_bindings.models.fetch_data_job_spec import FetchDataJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of FetchDataJobSpec from a JSON string
fetch_data_job_spec_instance = FetchDataJobSpec.from_json(json)
# print the JSON string representation of the object
print(FetchDataJobSpec.to_json())

# convert the object into a dict
fetch_data_job_spec_dict = fetch_data_job_spec_instance.to_dict()
# create an instance of FetchDataJobSpec from a dict
fetch_data_job_spec_from_dict = FetchDataJobSpec.from_dict(fetch_data_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


