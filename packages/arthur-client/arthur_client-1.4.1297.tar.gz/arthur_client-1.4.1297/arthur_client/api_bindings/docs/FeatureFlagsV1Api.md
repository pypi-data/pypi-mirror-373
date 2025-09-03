# arthur_client.api_bindings.FeatureFlagsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_feature_flags**](FeatureFlagsV1Api.md#get_feature_flags) | **GET** /api/v1/feature-flags | Get Feature Flags.


# **get_feature_flags**
> Dict[str, object] get_feature_flags()

Get Feature Flags.

Retrieves all feature flags in the environment.

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
    api_instance = arthur_client.api_bindings.FeatureFlagsV1Api(api_client)

    try:
        # Get Feature Flags.
        api_response = api_instance.get_feature_flags()
        print("The response of FeatureFlagsV1Api->get_feature_flags:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FeatureFlagsV1Api->get_feature_flags: %s\n" % e)
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

