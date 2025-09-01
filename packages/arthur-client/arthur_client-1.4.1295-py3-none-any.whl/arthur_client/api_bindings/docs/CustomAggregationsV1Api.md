# arthur_client.api_bindings.CustomAggregationsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_custom_aggregation**](CustomAggregationsV1Api.md#delete_custom_aggregation) | **DELETE** /api/v1/custom_aggregations/{custom_aggregation_id} | Delete Custom Aggregation.
[**get_custom_aggregation**](CustomAggregationsV1Api.md#get_custom_aggregation) | **GET** /api/v1/custom_aggregations/{custom_aggregation_id} | Get Custom Aggregation By Id.
[**get_custom_aggregations_for_workspace**](CustomAggregationsV1Api.md#get_custom_aggregations_for_workspace) | **GET** /api/v1/workspaces/{workspace_id}/custom_aggregations | Get Custom Aggregation.
[**post_custom_aggregation**](CustomAggregationsV1Api.md#post_custom_aggregation) | **POST** /api/v1/workspaces/{workspace_id}/custom_aggregations | Post Custom Aggregation.
[**put_custom_aggregation**](CustomAggregationsV1Api.md#put_custom_aggregation) | **PUT** /api/v1/custom_aggregations/{custom_aggregation_id} | Update Custom Aggregation By Id.
[**validate_custom_aggregation**](CustomAggregationsV1Api.md#validate_custom_aggregation) | **POST** /api/v1/workspaces/{workspace_id}/validate_custom_aggregation | Validate A Custom Aggregation Before Creation.


# **delete_custom_aggregation**
> delete_custom_aggregation(custom_aggregation_id)

Delete Custom Aggregation.

Requires custom_aggregation_delete permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    custom_aggregation_id = 'custom_aggregation_id_example' # str | 

    try:
        # Delete Custom Aggregation.
        api_instance.delete_custom_aggregation(custom_aggregation_id)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->delete_custom_aggregation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_aggregation_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_custom_aggregation**
> CustomAggregationSpecSchema get_custom_aggregation(custom_aggregation_id, version=version, latest=latest)

Get Custom Aggregation By Id.

Requires custom_aggregation_read permission. Includes version filters to specify the versions included on the returned aggregation.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.custom_aggregation_spec_schema import CustomAggregationSpecSchema
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    custom_aggregation_id = 'custom_aggregation_id_example' # str | 
    version = 56 # int | The version of the custom aggregation to fetch. (optional)
    latest = False # bool | Whether to fetch the latest version of the custom aggregation. (optional) (default to False)

    try:
        # Get Custom Aggregation By Id.
        api_response = api_instance.get_custom_aggregation(custom_aggregation_id, version=version, latest=latest)
        print("The response of CustomAggregationsV1Api->get_custom_aggregation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->get_custom_aggregation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_aggregation_id** | **str**|  | 
 **version** | **int**| The version of the custom aggregation to fetch. | [optional] 
 **latest** | **bool**| Whether to fetch the latest version of the custom aggregation. | [optional] [default to False]

### Return type

[**CustomAggregationSpecSchema**](CustomAggregationSpecSchema.md)

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

# **get_custom_aggregations_for_workspace**
> ResourceListCustomAggregationSpecSchema get_custom_aggregations_for_workspace(workspace_id, page=page, page_size=page_size)

Get Custom Aggregation.

Requires workspace_list_custom_aggregations permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_custom_aggregation_spec_schema import ResourceListCustomAggregationSpecSchema
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    page = 1 # int | The page number to fetch. (optional) (default to 1)
    page_size = 10 # int | The number of items per page. (optional) (default to 10)

    try:
        # Get Custom Aggregation.
        api_response = api_instance.get_custom_aggregations_for_workspace(workspace_id, page=page, page_size=page_size)
        print("The response of CustomAggregationsV1Api->get_custom_aggregations_for_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->get_custom_aggregations_for_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **page** | **int**| The page number to fetch. | [optional] [default to 1]
 **page_size** | **int**| The number of items per page. | [optional] [default to 10]

### Return type

[**ResourceListCustomAggregationSpecSchema**](ResourceListCustomAggregationSpecSchema.md)

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

# **post_custom_aggregation**
> CustomAggregationSpecSchema post_custom_aggregation(workspace_id, post_custom_aggregation_spec_schema)

Post Custom Aggregation.

Requires workspace_create_custom_aggregation permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.custom_aggregation_spec_schema import CustomAggregationSpecSchema
from arthur_client.api_bindings.models.post_custom_aggregation_spec_schema import PostCustomAggregationSpecSchema
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_custom_aggregation_spec_schema = arthur_client.api_bindings.PostCustomAggregationSpecSchema() # PostCustomAggregationSpecSchema | 

    try:
        # Post Custom Aggregation.
        api_response = api_instance.post_custom_aggregation(workspace_id, post_custom_aggregation_spec_schema)
        print("The response of CustomAggregationsV1Api->post_custom_aggregation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->post_custom_aggregation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_custom_aggregation_spec_schema** | [**PostCustomAggregationSpecSchema**](PostCustomAggregationSpecSchema.md)|  | 

### Return type

[**CustomAggregationSpecSchema**](CustomAggregationSpecSchema.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_custom_aggregation**
> CustomAggregationSpecSchema put_custom_aggregation(custom_aggregation_id, put_custom_aggregation_spec_schema)

Update Custom Aggregation By Id.

Creates a new version of the custom aggregation. Requires custom_aggregation_put permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.custom_aggregation_spec_schema import CustomAggregationSpecSchema
from arthur_client.api_bindings.models.put_custom_aggregation_spec_schema import PutCustomAggregationSpecSchema
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    custom_aggregation_id = 'custom_aggregation_id_example' # str | 
    put_custom_aggregation_spec_schema = arthur_client.api_bindings.PutCustomAggregationSpecSchema() # PutCustomAggregationSpecSchema | 

    try:
        # Update Custom Aggregation By Id.
        api_response = api_instance.put_custom_aggregation(custom_aggregation_id, put_custom_aggregation_spec_schema)
        print("The response of CustomAggregationsV1Api->put_custom_aggregation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->put_custom_aggregation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **custom_aggregation_id** | **str**|  | 
 **put_custom_aggregation_spec_schema** | [**PutCustomAggregationSpecSchema**](PutCustomAggregationSpecSchema.md)|  | 

### Return type

[**CustomAggregationSpecSchema**](CustomAggregationSpecSchema.md)

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

# **validate_custom_aggregation**
> ValidationResults validate_custom_aggregation(workspace_id, post_custom_aggregation_spec_schema)

Validate A Custom Aggregation Before Creation.

Validates the custom aggregation and returns any expected errors for aggregation creation. Requires workspace_validate_custom_aggregation permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_custom_aggregation_spec_schema import PostCustomAggregationSpecSchema
from arthur_client.api_bindings.models.validation_results import ValidationResults
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
    api_instance = arthur_client.api_bindings.CustomAggregationsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_custom_aggregation_spec_schema = arthur_client.api_bindings.PostCustomAggregationSpecSchema() # PostCustomAggregationSpecSchema | 

    try:
        # Validate A Custom Aggregation Before Creation.
        api_response = api_instance.validate_custom_aggregation(workspace_id, post_custom_aggregation_spec_schema)
        print("The response of CustomAggregationsV1Api->validate_custom_aggregation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomAggregationsV1Api->validate_custom_aggregation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_custom_aggregation_spec_schema** | [**PostCustomAggregationSpecSchema**](PostCustomAggregationSpecSchema.md)|  | 

### Return type

[**ValidationResults**](ValidationResults.md)

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

