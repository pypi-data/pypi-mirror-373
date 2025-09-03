# arthur_client.api_bindings.RegistrationV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**post_sign_up_user**](RegistrationV1Api.md#post_sign_up_user) | **POST** /api/v1/sign-up | Sign Up New User.


# **post_sign_up_user**
> object post_sign_up_user(register_user)

Sign Up New User.

Signs up a new user and creates default resources. Triggers invitation to user email. Account creation feature flag must be enabled to use this endpoint.

### Example


```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.register_user import RegisterUser
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
    api_instance = arthur_client.api_bindings.RegistrationV1Api(api_client)
    register_user = arthur_client.api_bindings.RegisterUser() # RegisterUser | 

    try:
        # Sign Up New User.
        api_response = api_instance.post_sign_up_user(register_user)
        print("The response of RegistrationV1Api->post_sign_up_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RegistrationV1Api->post_sign_up_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **register_user** | [**RegisterUser**](RegisterUser.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

