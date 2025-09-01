# arthur_client.api_bindings.ConnectorSchemasV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_connector_schema_by_type**](ConnectorSchemasV1Api.md#get_connector_schema_by_type) | **GET** /api/v1/connector_schemas/{connector_type} | Get Connector Schema By Type
[**get_connector_types**](ConnectorSchemasV1Api.md#get_connector_types) | **GET** /api/v1/connector_schemas/connector_types | Get Available Connector Types


# **get_connector_schema_by_type**
> ConnectorSpecSchema get_connector_schema_by_type(connector_type)

Get Connector Schema By Type

Returns a connector schema by type.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_spec_schema import ConnectorSpecSchema
from arthur_client.api_bindings.models.connector_type import ConnectorType
from arthur_client.api_bindings.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = arthur_client.api_bindings.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with arthur_client.api_bindings.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = arthur_client.api_bindings.ConnectorSchemasV1Api(api_client)
    connector_type = arthur_client.api_bindings.ConnectorType() # ConnectorType | The type of the connector schema to fetch.

    try:
        # Get Connector Schema By Type
        api_response = api_instance.get_connector_schema_by_type(connector_type)
        print("The response of ConnectorSchemasV1Api->get_connector_schema_by_type:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorSchemasV1Api->get_connector_schema_by_type: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_type** | [**ConnectorType**](.md)| The type of the connector schema to fetch. | 

### Return type

[**ConnectorSpecSchema**](ConnectorSpecSchema.md)

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connector_types**
> ResourceListConnectorType get_connector_types()

Get Available Connector Types

Returns all Arthur-supported connector types.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_connector_type import ResourceListConnectorType
from arthur_client.api_bindings.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = arthur_client.api_bindings.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with arthur_client.api_bindings.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = arthur_client.api_bindings.ConnectorSchemasV1Api(api_client)

    try:
        # Get Available Connector Types
        api_response = api_instance.get_connector_types()
        print("The response of ConnectorSchemasV1Api->get_connector_types:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorSchemasV1Api->get_connector_types: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ResourceListConnectorType**](ResourceListConnectorType.md)

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

