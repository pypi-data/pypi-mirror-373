# DataRetrievalOperation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Operation ID used for tracking the state of the operation. | 
**job_id** | **str** | Job ID executing the data retrieval. | 
**status** | [**DataRetrievalStatus**](DataRetrievalStatus.md) | Current status of the retrieval operation. | 
**data** | [**DataRetrievalData**](DataRetrievalData.md) |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.data_retrieval_operation import DataRetrievalOperation

# TODO update the JSON string below
json = "{}"
# create an instance of DataRetrievalOperation from a JSON string
data_retrieval_operation_instance = DataRetrievalOperation.from_json(json)
# print the JSON string representation of the object
print(DataRetrievalOperation.to_json())

# convert the object into a dict
data_retrieval_operation_dict = data_retrieval_operation_instance.to_dict()
# create an instance of DataRetrievalOperation from a dict
data_retrieval_operation_from_dict = DataRetrievalOperation.from_dict(data_retrieval_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


