# InfiniteResourceListAlert


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Alert]**](Alert.md) | List of records. | 
**pagination** | [**InfinitePagination**](InfinitePagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.infinite_resource_list_alert import InfiniteResourceListAlert

# TODO update the JSON string below
json = "{}"
# create an instance of InfiniteResourceListAlert from a JSON string
infinite_resource_list_alert_instance = InfiniteResourceListAlert.from_json(json)
# print the JSON string representation of the object
print(InfiniteResourceListAlert.to_json())

# convert the object into a dict
infinite_resource_list_alert_dict = infinite_resource_list_alert_instance.to_dict()
# create an instance of InfiniteResourceListAlert from a dict
infinite_resource_list_alert_from_dict = InfiniteResourceListAlert.from_dict(infinite_resource_list_alert_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


