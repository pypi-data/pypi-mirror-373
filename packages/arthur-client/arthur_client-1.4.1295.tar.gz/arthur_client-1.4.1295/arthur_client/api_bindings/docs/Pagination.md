# Pagination


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** | The current page number. Page 1 is the first page. | [optional] [default to 1]
**page_size** | **int** | Number of records per page. | [optional] [default to 20]
**total_pages** | **int** | Total number of pages. | 
**total_records** | **int** | Total number of records across all pages. | 

## Example

```python
from arthur_client.api_bindings.models.pagination import Pagination

# TODO update the JSON string below
json = "{}"
# create an instance of Pagination from a JSON string
pagination_instance = Pagination.from_json(json)
# print the JSON string representation of the object
print(Pagination.to_json())

# convert the object into a dict
pagination_dict = pagination_instance.to_dict()
# create an instance of Pagination from a dict
pagination_from_dict = Pagination.from_dict(pagination_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


