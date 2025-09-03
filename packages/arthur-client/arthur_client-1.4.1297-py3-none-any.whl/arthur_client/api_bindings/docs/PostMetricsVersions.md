# PostMetricsVersions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**range_start** | **datetime** | Start timestamp of the metrics range included in this metric version. | 
**range_end** | **datetime** | End timestamp of the metrics range included in this metric version. | 

## Example

```python
from arthur_client.api_bindings.models.post_metrics_versions import PostMetricsVersions

# TODO update the JSON string below
json = "{}"
# create an instance of PostMetricsVersions from a JSON string
post_metrics_versions_instance = PostMetricsVersions.from_json(json)
# print the JSON string representation of the object
print(PostMetricsVersions.to_json())

# convert the object into a dict
post_metrics_versions_dict = post_metrics_versions_instance.to_dict()
# create an instance of PostMetricsVersions from a dict
post_metrics_versions_from_dict = PostMetricsVersions.from_dict(post_metrics_versions_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


