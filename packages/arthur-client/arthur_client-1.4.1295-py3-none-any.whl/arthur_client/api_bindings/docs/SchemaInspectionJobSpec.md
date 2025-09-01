# SchemaInspectionJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'schema_inspection']
**connector_id** | **str** | The id of the connector to list datasets. | 
**available_dataset_id** | **str** | The id of the dataset within the connector to inspect the schema. | 

## Example

```python
from arthur_client.api_bindings.models.schema_inspection_job_spec import SchemaInspectionJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaInspectionJobSpec from a JSON string
schema_inspection_job_spec_instance = SchemaInspectionJobSpec.from_json(json)
# print the JSON string representation of the object
print(SchemaInspectionJobSpec.to_json())

# convert the object into a dict
schema_inspection_job_spec_dict = schema_inspection_job_spec_instance.to_dict()
# create an instance of SchemaInspectionJobSpec from a dict
schema_inspection_job_spec_from_dict = SchemaInspectionJobSpec.from_dict(schema_inspection_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


