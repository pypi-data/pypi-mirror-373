# InfinitePagination


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** | The current page number. Page 1 is the first page. | [optional] [default to 1]
**page_size** | **int** | Number of records per page. | [optional] [default to 20]

## Example

```python
from arthur_client.api_bindings.models.infinite_pagination import InfinitePagination

# TODO update the JSON string below
json = "{}"
# create an instance of InfinitePagination from a JSON string
infinite_pagination_instance = InfinitePagination.from_json(json)
# print the JSON string representation of the object
print(InfinitePagination.to_json())

# convert the object into a dict
infinite_pagination_dict = infinite_pagination_instance.to_dict()
# create an instance of InfinitePagination from a dict
infinite_pagination_from_dict = InfinitePagination.from_dict(infinite_pagination_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


