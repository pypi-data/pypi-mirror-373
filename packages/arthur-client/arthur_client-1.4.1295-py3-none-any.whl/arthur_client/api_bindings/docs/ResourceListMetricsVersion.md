# ResourceListMetricsVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[MetricsVersion]**](MetricsVersion.md) | List of records. | 
**pagination** | [**Pagination**](Pagination.md) | Pagination information. | 

## Example

```python
from arthur_client.api_bindings.models.resource_list_metrics_version import ResourceListMetricsVersion

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceListMetricsVersion from a JSON string
resource_list_metrics_version_instance = ResourceListMetricsVersion.from_json(json)
# print the JSON string representation of the object
print(ResourceListMetricsVersion.to_json())

# convert the object into a dict
resource_list_metrics_version_dict = resource_list_metrics_version_instance.to_dict()
# create an instance of ResourceListMetricsVersion from a dict
resource_list_metrics_version_from_dict = ResourceListMetricsVersion.from_dict(resource_list_metrics_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


