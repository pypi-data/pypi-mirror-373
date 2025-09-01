# ServiceAccountCredentials


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** | The service account client ID. | 
**client_secret** | **str** | The service account client secret. | 

## Example

```python
from arthur_client.api_bindings.models.service_account_credentials import ServiceAccountCredentials

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceAccountCredentials from a JSON string
service_account_credentials_instance = ServiceAccountCredentials.from_json(json)
# print the JSON string representation of the object
print(ServiceAccountCredentials.to_json())

# convert the object into a dict
service_account_credentials_dict = service_account_credentials_instance.to_dict()
# create an instance of ServiceAccountCredentials from a dict
service_account_credentials_from_dict = ServiceAccountCredentials.from_dict(service_account_credentials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


