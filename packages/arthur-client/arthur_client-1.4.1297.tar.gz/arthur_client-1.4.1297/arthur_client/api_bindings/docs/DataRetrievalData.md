# DataRetrievalData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** | Serialized content. | 
**data_schema** | **object** |  | 

## Example

```python
from arthur_client.api_bindings.models.data_retrieval_data import DataRetrievalData

# TODO update the JSON string below
json = "{}"
# create an instance of DataRetrievalData from a JSON string
data_retrieval_data_instance = DataRetrievalData.from_json(json)
# print the JSON string representation of the object
print(DataRetrievalData.to_json())

# convert the object into a dict
data_retrieval_data_dict = data_retrieval_data_instance.to_dict()
# create an instance of DataRetrievalData from a dict
data_retrieval_data_from_dict = DataRetrievalData.from_dict(data_retrieval_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


