# arthur_client.api_bindings.UpsolveV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**post_tenant**](UpsolveV1Api.md#post_tenant) | **POST** /api/v1/upsolve-ai/tenant/token | Retrieve Jwt For Upsolve Ai Dashboards


# **post_tenant**
> UpsolveToken post_tenant(post_upsolve_tenant)

Retrieve Jwt For Upsolve Ai Dashboards

Authenticates and authorizes user with Upsolve AI and returns Upsolve JWT.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_upsolve_tenant import PostUpsolveTenant
from arthur_client.api_bindings.models.upsolve_token import UpsolveToken
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
    api_instance = arthur_client.api_bindings.UpsolveV1Api(api_client)
    post_upsolve_tenant = arthur_client.api_bindings.PostUpsolveTenant() # PostUpsolveTenant | 

    try:
        # Retrieve Jwt For Upsolve Ai Dashboards
        api_response = api_instance.post_tenant(post_upsolve_tenant)
        print("The response of UpsolveV1Api->post_tenant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpsolveV1Api->post_tenant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_upsolve_tenant** | [**PostUpsolveTenant**](PostUpsolveTenant.md)|  | 

### Return type

[**UpsolveToken**](UpsolveToken.md)

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

