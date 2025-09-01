# PutRetrievedData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** | Serialized content. | 

## Example

```python
from arthur_client.api_bindings.models.put_retrieved_data import PutRetrievedData

# TODO update the JSON string below
json = "{}"
# create an instance of PutRetrievedData from a JSON string
put_retrieved_data_instance = PutRetrievedData.from_json(json)
# print the JSON string representation of the object
print(PutRetrievedData.to_json())

# convert the object into a dict
put_retrieved_data_dict = put_retrieved_data_instance.to_dict()
# create an instance of PutRetrievedData from a dict
put_retrieved_data_from_dict = PutRetrievedData.from_dict(put_retrieved_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


