# PostLinkTaskRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_id** | **str** | The id of the Shield task to link when creating the new model. | 
**connector_id** | **str** | The id of the connector with the task to link. The connector must be an engine internal connector. | 
**onboarding_identifier** | **str** |  | [optional] 

## Example

```python
from arthur_client.api_bindings.models.post_link_task_request import PostLinkTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostLinkTaskRequest from a JSON string
post_link_task_request_instance = PostLinkTaskRequest.from_json(json)
# print the JSON string representation of the object
print(PostLinkTaskRequest.to_json())

# convert the object into a dict
post_link_task_request_dict = post_link_task_request_instance.to_dict()
# create an instance of PostLinkTaskRequest from a dict
post_link_task_request_from_dict = PostLinkTaskRequest.from_dict(post_link_task_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


