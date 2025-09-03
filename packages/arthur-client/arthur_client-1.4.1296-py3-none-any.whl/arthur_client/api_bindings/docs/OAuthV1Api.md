# arthur_client.api_bindings.OAuthV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_openid_configuration**](OAuthV1Api.md#get_openid_configuration) | **GET** /api/v1/auth/oidc/.well-known/openid-configuration | Get Openid Configuration Metadata


# **get_openid_configuration**
> Dict[str, object] get_openid_configuration()

Get Openid Configuration Metadata

Returns well-known openid configuration for Arthur auth server

### Example


```python
import arthur_client.api_bindings
from arthur_client.api_bindings.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = arthur_client.api_bindings.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with arthur_client.api_bindings.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = arthur_client.api_bindings.OAuthV1Api(api_client)

    try:
        # Get Openid Configuration Metadata
        api_response = api_instance.get_openid_configuration()
        print("The response of OAuthV1Api->get_openid_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OAuthV1Api->get_openid_configuration: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

