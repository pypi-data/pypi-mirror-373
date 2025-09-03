# arthur_client.api_bindings.ConnectorsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_connector**](ConnectorsV1Api.md#delete_connector) | **DELETE** /api/v1/connectors/{connector_id} | Delete Connector
[**get_connector**](ConnectorsV1Api.md#get_connector) | **GET** /api/v1/connectors/{connector_id} | Get Connector
[**get_connectors**](ConnectorsV1Api.md#get_connectors) | **GET** /api/v1/projects/{project_id}/connectors | List Connectors
[**get_sensitive_connector**](ConnectorsV1Api.md#get_sensitive_connector) | **GET** /api/v1/connectors/{connector_id}/sensitive | Get Sensitive Connector
[**patch_connector**](ConnectorsV1Api.md#patch_connector) | **PATCH** /api/v1/connectors/{connector_id} | Update Connector
[**post_connector**](ConnectorsV1Api.md#post_connector) | **POST** /api/v1/projects/{project_id}/connectors | Create Connector
[**put_connector_check_results**](ConnectorsV1Api.md#put_connector_check_results) | **PUT** /api/v1/connectors/{connector_id}/check_results | Persist Connector Check Results


# **delete_connector**
> delete_connector(connector_id)

Delete Connector

Deletes a single connector by id. Requires connector_delete permission.

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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 

    try:
        # Delete Connector
        api_instance.delete_connector(connector_id)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->delete_connector: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 

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
**204** | No Content |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connector**
> ConnectorSpec get_connector(connector_id)

Get Connector

Returns a single connector by ID. Requires connector_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_spec import ConnectorSpec
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 

    try:
        # Get Connector
        api_response = api_instance.get_connector(connector_id)
        print("The response of ConnectorsV1Api->get_connector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->get_connector: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 

### Return type

[**ConnectorSpec**](ConnectorSpec.md)

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

# **get_connectors**
> ResourceListConnectorSpec get_connectors(project_id, sort=sort, order=order, connector_type=connector_type, name=name, data_plane_id=data_plane_id, include_temporary_connectors=include_temporary_connectors, page=page, page_size=page_size)

List Connectors

Returns connectors matching the filter and sorting criteria. If multiple filters are specified, results will only be returned that match all of the specified criteria. Requires project_list_connectors permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_type import ConnectorType
from arthur_client.api_bindings.models.connectors_sort import ConnectorsSort
from arthur_client.api_bindings.models.resource_list_connector_spec import ResourceListConnectorSpec
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    sort = arthur_client.api_bindings.ConnectorsSort() # ConnectorsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    connector_type = arthur_client.api_bindings.ConnectorType() # ConnectorType | Filter the results for connectors with this connector type. Optional. (optional)
    name = 'name_example' # str | Filter the results for connectors with a name similar to this name. Optional. (optional)
    data_plane_id = 'data_plane_id_example' # str | Filter the results for connectors with this data plane ID. Optional. (optional)
    include_temporary_connectors = False # bool | Include connectors marked as temporary (for testing only) in the results. Optional. (optional) (default to False)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Connectors
        api_response = api_instance.get_connectors(project_id, sort=sort, order=order, connector_type=connector_type, name=name, data_plane_id=data_plane_id, include_temporary_connectors=include_temporary_connectors, page=page, page_size=page_size)
        print("The response of ConnectorsV1Api->get_connectors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->get_connectors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sort** | [**ConnectorsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **connector_type** | [**ConnectorType**](.md)| Filter the results for connectors with this connector type. Optional. | [optional] 
 **name** | **str**| Filter the results for connectors with a name similar to this name. Optional. | [optional] 
 **data_plane_id** | **str**| Filter the results for connectors with this data plane ID. Optional. | [optional] 
 **include_temporary_connectors** | **bool**| Include connectors marked as temporary (for testing only) in the results. Optional. | [optional] [default to False]
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListConnectorSpec**](ResourceListConnectorSpec.md)

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

# **get_sensitive_connector**
> ConnectorSpec get_sensitive_connector(connector_id)

Get Sensitive Connector

Returns a single connector by ID with unmasked sensitive fields. Requires connector_get_sensitive_fields permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_spec import ConnectorSpec
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 

    try:
        # Get Sensitive Connector
        api_response = api_instance.get_sensitive_connector(connector_id)
        print("The response of ConnectorsV1Api->get_sensitive_connector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->get_sensitive_connector: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 

### Return type

[**ConnectorSpec**](ConnectorSpec.md)

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

# **patch_connector**
> ConnectorSpec patch_connector(connector_id, patch_connector_spec)

Update Connector

Updates a single connector. Requires connector_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_spec import ConnectorSpec
from arthur_client.api_bindings.models.patch_connector_spec import PatchConnectorSpec
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    patch_connector_spec = arthur_client.api_bindings.PatchConnectorSpec() # PatchConnectorSpec | 

    try:
        # Update Connector
        api_response = api_instance.patch_connector(connector_id, patch_connector_spec)
        print("The response of ConnectorsV1Api->patch_connector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->patch_connector: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **patch_connector_spec** | [**PatchConnectorSpec**](PatchConnectorSpec.md)|  | 

### Return type

[**ConnectorSpec**](ConnectorSpec.md)

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

# **post_connector**
> ConnectorSpec post_connector(project_id, post_connector_spec)

Create Connector

Creates a single connector. Requires project_create_connector permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_spec import ConnectorSpec
from arthur_client.api_bindings.models.post_connector_spec import PostConnectorSpec
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_connector_spec = arthur_client.api_bindings.PostConnectorSpec() # PostConnectorSpec | 

    try:
        # Create Connector
        api_response = api_instance.post_connector(project_id, post_connector_spec)
        print("The response of ConnectorsV1Api->post_connector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->post_connector: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_connector_spec** | [**PostConnectorSpec**](PostConnectorSpec.md)|  | 

### Return type

[**ConnectorSpec**](ConnectorSpec.md)

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

# **put_connector_check_results**
> put_connector_check_results(connector_id, connector_check_result)

Persist Connector Check Results

Sets the check result of the connector. Requires connector_put_check_result permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_check_result import ConnectorCheckResult
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
    api_instance = arthur_client.api_bindings.ConnectorsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    connector_check_result = arthur_client.api_bindings.ConnectorCheckResult() # ConnectorCheckResult | 

    try:
        # Persist Connector Check Results
        api_instance.put_connector_check_results(connector_id, connector_check_result)
    except Exception as e:
        print("Exception when calling ConnectorsV1Api->put_connector_check_results: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **connector_check_result** | [**ConnectorCheckResult**](ConnectorCheckResult.md)|  | 

### Return type

void (empty response body)

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

