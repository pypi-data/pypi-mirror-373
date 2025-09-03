# Project


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Time of record creation. | 
**updated_at** | **datetime** | Time of last record update. | 
**id** | **str** | ID of the project. | 
**name** | **str** | Name of the project. | 
**description** | **str** |  | [optional] 
**workspace_id** | **str** | ID of the parent workspace. | 
**total_artifacts** | **int** | Count of artifacts in the project. Current supported artifacts are: models, including shield tasks and bench test suites. | 

## Example

```python
from arthur_client.api_bindings.models.project import Project

# TODO update the JSON string below
json = "{}"
# create an instance of Project from a JSON string
project_instance = Project.from_json(json)
# print the JSON string representation of the object
print(Project.to_json())

# convert the object into a dict
project_dict = project_instance.to_dict()
# create an instance of Project from a dict
project_from_dict = Project.from_dict(project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


