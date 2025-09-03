# arthur_client.api_bindings.DataPlanesV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_data_plane**](DataPlanesV1Api.md#delete_data_plane) | **DELETE** /api/v1/data_planes/{data_plane_id} | Delete Data Plane By Id
[**get_data_plane**](DataPlanesV1Api.md#get_data_plane) | **GET** /api/v1/data_planes/{data_plane_id} | Get Data Plane By Id
[**get_data_planes**](DataPlanesV1Api.md#get_data_planes) | **GET** /api/v1/workspaces/{workspace_id}/data_planes | Get Data Planes.
[**patch_data_plane**](DataPlanesV1Api.md#patch_data_plane) | **PATCH** /api/v1/data_planes/{data_plane_id} | Update Data Plane
[**post_data_plane**](DataPlanesV1Api.md#post_data_plane) | **POST** /api/v1/workspaces/{workspace_id}/data_planes | Post Data Plane.
[**post_data_plane_cred_set**](DataPlanesV1Api.md#post_data_plane_cred_set) | **POST** /api/v1/data_planes/{data_plane_id}/credential_set | Regenerate Data Plane Credential Set.


# **delete_data_plane**
> delete_data_plane(data_plane_id)

Delete Data Plane By Id

Deletes a single data plane. Requires data_plane_delete permission.

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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 

    try:
        # Delete Data Plane By Id
        api_instance.delete_data_plane(data_plane_id)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->delete_data_plane: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 

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

# **get_data_plane**
> DataPlane get_data_plane(data_plane_id)

Get Data Plane By Id

Returns a single data plane by ID. Requires data_plane_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane import DataPlane
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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 

    try:
        # Get Data Plane By Id
        api_response = api_instance.get_data_plane(data_plane_id)
        print("The response of DataPlanesV1Api->get_data_plane:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->get_data_plane: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 

### Return type

[**DataPlane**](DataPlane.md)

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

# **get_data_planes**
> ResourceListDataPlane get_data_planes(workspace_id, sort=sort, order=order, name=name, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)

Get Data Planes.

Requires workspace_list_data_planes permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane_sort import DataPlaneSort
from arthur_client.api_bindings.models.resource_list_data_plane import ResourceListDataPlane
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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    sort = arthur_client.api_bindings.DataPlaneSort() # DataPlaneSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    name = 'name_example' # str | Search term to filter workspaces by name. (optional)
    gen_ai_enabled = True # bool | Filter to only return engines enabled with the GenAI capability (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Data Planes.
        api_response = api_instance.get_data_planes(workspace_id, sort=sort, order=order, name=name, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)
        print("The response of DataPlanesV1Api->get_data_planes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->get_data_planes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **sort** | [**DataPlaneSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **name** | **str**| Search term to filter workspaces by name. | [optional] 
 **gen_ai_enabled** | **bool**| Filter to only return engines enabled with the GenAI capability | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataPlane**](ResourceListDataPlane.md)

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

# **patch_data_plane**
> DataPlane patch_data_plane(data_plane_id, patch_data_plane)

Update Data Plane

Updates a single data plane. Requires data_plane_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane import DataPlane
from arthur_client.api_bindings.models.patch_data_plane import PatchDataPlane
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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 
    patch_data_plane = arthur_client.api_bindings.PatchDataPlane() # PatchDataPlane | 

    try:
        # Update Data Plane
        api_response = api_instance.patch_data_plane(data_plane_id, patch_data_plane)
        print("The response of DataPlanesV1Api->patch_data_plane:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->patch_data_plane: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 
 **patch_data_plane** | [**PatchDataPlane**](PatchDataPlane.md)|  | 

### Return type

[**DataPlane**](DataPlane.md)

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

# **post_data_plane**
> SensitiveDataPlane post_data_plane(workspace_id, post_data_plane)

Post Data Plane.

Requires workspace_create_data_plane permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_data_plane import PostDataPlane
from arthur_client.api_bindings.models.sensitive_data_plane import SensitiveDataPlane
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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_data_plane = arthur_client.api_bindings.PostDataPlane() # PostDataPlane | 

    try:
        # Post Data Plane.
        api_response = api_instance.post_data_plane(workspace_id, post_data_plane)
        print("The response of DataPlanesV1Api->post_data_plane:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->post_data_plane: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_data_plane** | [**PostDataPlane**](PostDataPlane.md)|  | 

### Return type

[**SensitiveDataPlane**](SensitiveDataPlane.md)

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

# **post_data_plane_cred_set**
> SensitiveDataPlane post_data_plane_cred_set(data_plane_id)

Regenerate Data Plane Credential Set.

Requires data_plane_regenerate_creds permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.sensitive_data_plane import SensitiveDataPlane
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
    api_instance = arthur_client.api_bindings.DataPlanesV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 

    try:
        # Regenerate Data Plane Credential Set.
        api_response = api_instance.post_data_plane_cred_set(data_plane_id)
        print("The response of DataPlanesV1Api->post_data_plane_cred_set:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlanesV1Api->post_data_plane_cred_set: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 

### Return type

[**SensitiveDataPlane**](SensitiveDataPlane.md)

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

