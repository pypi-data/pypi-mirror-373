# arthur_client.api_bindings.MetricsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_model_metrics_versions**](MetricsV1Api.md#get_model_metrics_versions) | **GET** /api/v1/models/{model_id}/metrics/versions | Get Metric Versions
[**post_model_metrics_by_version**](MetricsV1Api.md#post_model_metrics_by_version) | **POST** /api/v1/models/{model_id}/metrics/versions/{metric_version_num} | Upload Metrics For Version
[**post_model_metrics_query**](MetricsV1Api.md#post_model_metrics_query) | **POST** /api/v1/models/{model_id}/metrics/query | Query Model Metrics
[**post_model_metrics_version**](MetricsV1Api.md#post_model_metrics_version) | **POST** /api/v1/models/{model_id}/metrics/versions | Create A Metric Version


# **get_model_metrics_versions**
> ResourceListMetricsVersion get_model_metrics_versions(model_id, sort=sort, order=order, page=page, page_size=page_size)

Get Metric Versions

Get metric versions for a model. Requires model_list_metric_versions permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.metrics_versions_sort import MetricsVersionsSort
from arthur_client.api_bindings.models.resource_list_metrics_version import ResourceListMetricsVersion
from arthur_client.api_bindings.models.sort_order import SortOrder
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
    api_instance = arthur_client.api_bindings.MetricsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    sort = arthur_client.api_bindings.MetricsVersionsSort() # MetricsVersionsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Metric Versions
        api_response = api_instance.get_model_metrics_versions(model_id, sort=sort, order=order, page=page, page_size=page_size)
        print("The response of MetricsV1Api->get_model_metrics_versions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetricsV1Api->get_model_metrics_versions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **sort** | [**MetricsVersionsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListMetricsVersion**](ResourceListMetricsVersion.md)

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

# **post_model_metrics_by_version**
> MetricsUploadResult post_model_metrics_by_version(model_id, metric_version_num, metrics_upload)

Upload Metrics For Version

Adds metrics for a model by version. This will create the version if it does not exist. Requires model_add_metrics_for_version permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.metrics_upload import MetricsUpload
from arthur_client.api_bindings.models.metrics_upload_result import MetricsUploadResult
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
    api_instance = arthur_client.api_bindings.MetricsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    metric_version_num = 56 # int | The version number for the metrics being uploaded. Should be an integer.
    metrics_upload = arthur_client.api_bindings.MetricsUpload() # MetricsUpload | 

    try:
        # Upload Metrics For Version
        api_response = api_instance.post_model_metrics_by_version(model_id, metric_version_num, metrics_upload)
        print("The response of MetricsV1Api->post_model_metrics_by_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetricsV1Api->post_model_metrics_by_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **metric_version_num** | **int**| The version number for the metrics being uploaded. Should be an integer. | 
 **metrics_upload** | [**MetricsUpload**](MetricsUpload.md)|  | 

### Return type

[**MetricsUploadResult**](MetricsUploadResult.md)

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

# **post_model_metrics_query**
> MetricsQueryResult post_model_metrics_query(model_id, post_metrics_query)

Query Model Metrics

Queries metrics for a model. Requires model_query_metrics permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.metrics_query_result import MetricsQueryResult
from arthur_client.api_bindings.models.post_metrics_query import PostMetricsQuery
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
    api_instance = arthur_client.api_bindings.MetricsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    post_metrics_query = arthur_client.api_bindings.PostMetricsQuery() # PostMetricsQuery | 

    try:
        # Query Model Metrics
        api_response = api_instance.post_model_metrics_query(model_id, post_metrics_query)
        print("The response of MetricsV1Api->post_model_metrics_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetricsV1Api->post_model_metrics_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **post_metrics_query** | [**PostMetricsQuery**](PostMetricsQuery.md)|  | 

### Return type

[**MetricsQueryResult**](MetricsQueryResult.md)

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
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_model_metrics_version**
> MetricsVersion post_model_metrics_version(model_id, post_metrics_versions)

Create A Metric Version

Creates a new version for metrics to be uploaded for this model. Requires model_create_metric_version permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.metrics_version import MetricsVersion
from arthur_client.api_bindings.models.post_metrics_versions import PostMetricsVersions
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
    api_instance = arthur_client.api_bindings.MetricsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    post_metrics_versions = arthur_client.api_bindings.PostMetricsVersions() # PostMetricsVersions | 

    try:
        # Create A Metric Version
        api_response = api_instance.post_model_metrics_version(model_id, post_metrics_versions)
        print("The response of MetricsV1Api->post_model_metrics_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetricsV1Api->post_model_metrics_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **post_metrics_versions** | [**PostMetricsVersions**](PostMetricsVersions.md)|  | 

### Return type

[**MetricsVersion**](MetricsVersion.md)

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

