# PostDataRetrievalOperation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start_timestamp** | **datetime** | Start timestamp to retrieve data for. | 
**end_timestamp** | **datetime** | End timestamp to retrieve data for. | 
**data_retrieval_filters** | [**List[DataResultFilter]**](DataResultFilter.md) | Filters to apply to retrieved data | [optional] [default to []]
**pagination_options** | [**ConnectorPaginationOptions**](ConnectorPaginationOptions.md) | Pagination options to apply to retrieved data | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_data_retrieval_operation import PostDataRetrievalOperation

# TODO update the JSON string below
json = "{}"
# create an instance of PostDataRetrievalOperation from a JSON string
post_data_retrieval_operation_instance = PostDataRetrievalOperation.from_json(json)
# print the JSON string representation of the object
print(PostDataRetrievalOperation.to_json())

# convert the object into a dict
post_data_retrieval_operation_dict = post_data_retrieval_operation_instance.to_dict()
# create an instance of PostDataRetrievalOperation from a dict
post_data_retrieval_operation_from_dict = PostDataRetrievalOperation.from_dict(post_data_retrieval_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


