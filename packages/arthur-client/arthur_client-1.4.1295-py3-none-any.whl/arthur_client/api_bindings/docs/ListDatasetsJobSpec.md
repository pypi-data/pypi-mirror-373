# ListDatasetsJobSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_type** | **str** |  | [optional] [default to 'list_datasets']
**connector_id** | **str** | The id of the connector to list datasets. | 

## Example

```python
from arthur_client.api_bindings.models.list_datasets_job_spec import ListDatasetsJobSpec

# TODO update the JSON string below
json = "{}"
# create an instance of ListDatasetsJobSpec from a JSON string
list_datasets_job_spec_instance = ListDatasetsJobSpec.from_json(json)
# print the JSON string representation of the object
print(ListDatasetsJobSpec.to_json())

# convert the object into a dict
list_datasets_job_spec_dict = list_datasets_job_spec_instance.to_dict()
# create an instance of ListDatasetsJobSpec from a dict
list_datasets_job_spec_from_dict = ListDatasetsJobSpec.from_dict(list_datasets_job_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


