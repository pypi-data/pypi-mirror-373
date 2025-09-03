# PostTaskRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the task | 
**connector_id** | **str** | The id of the connector where the task will be created. The connector must be an engine internal connector. | 
**onboarding_identifier** | **str** |  | [optional] 
**rules_to_add** | [**List[NewRuleRequest]**](NewRuleRequest.md) | List of rules to add to the task. | [optional] 
**is_agentic** | **bool** | Whether this task should be created as an agentic trace task. If True, no rules will be applied to the task. | [optional] [default to False]

## Example

```python
from arthur_client.api_bindings.models.post_task_request import PostTaskRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostTaskRequest from a JSON string
post_task_request_instance = PostTaskRequest.from_json(json)
# print the JSON string representation of the object
print(PostTaskRequest.to_json())

# convert the object into a dict
post_task_request_dict = post_task_request_instance.to_dict()
# create an instance of PostTaskRequest from a dict
post_task_request_from_dict = PostTaskRequest.from_dict(post_task_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


