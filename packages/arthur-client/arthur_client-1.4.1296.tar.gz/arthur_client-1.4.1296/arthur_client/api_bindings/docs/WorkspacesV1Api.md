# arthur_client.api_bindings.WorkspacesV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_workspace**](WorkspacesV1Api.md#delete_workspace) | **DELETE** /api/v1/workspaces/{workspace_id} | Delete Workspace.
[**get_workspace**](WorkspacesV1Api.md#get_workspace) | **GET** /api/v1/workspaces/{workspace_id} | Get Workspace.
[**get_workspaces**](WorkspacesV1Api.md#get_workspaces) | **GET** /api/v1/organization/workspaces | Get Workspaces.
[**patch_workspace**](WorkspacesV1Api.md#patch_workspace) | **PATCH** /api/v1/workspaces/{workspace_id} | Patch Workspace.
[**post_workspace**](WorkspacesV1Api.md#post_workspace) | **POST** /api/v1/organization/workspaces | Post Workspace.


# **delete_workspace**
> delete_workspace(workspace_id)

Delete Workspace.

Requires workspace_delete permission.

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
    api_instance = arthur_client.api_bindings.WorkspacesV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 

    try:
        # Delete Workspace.
        api_instance.delete_workspace(workspace_id)
    except Exception as e:
        print("Exception when calling WorkspacesV1Api->delete_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 

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
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workspace**
> Workspace get_workspace(workspace_id)

Get Workspace.

Requires workspace_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.workspace import Workspace
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
    api_instance = arthur_client.api_bindings.WorkspacesV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 

    try:
        # Get Workspace.
        api_response = api_instance.get_workspace(workspace_id)
        print("The response of WorkspacesV1Api->get_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesV1Api->get_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 

### Return type

[**Workspace**](Workspace.md)

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

# **get_workspaces**
> ResourceListWorkspace get_workspaces(sort=sort, order=order, name=name, page=page, page_size=page_size)

Get Workspaces.

Requires organization_list_workspaces permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_workspace import ResourceListWorkspace
from arthur_client.api_bindings.models.sort_order import SortOrder
from arthur_client.api_bindings.models.workspace_sort import WorkspaceSort
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
    api_instance = arthur_client.api_bindings.WorkspacesV1Api(api_client)
    sort = arthur_client.api_bindings.WorkspaceSort() # WorkspaceSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    name = 'name_example' # str | Search term to filter workspaces by name. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Workspaces.
        api_response = api_instance.get_workspaces(sort=sort, order=order, name=name, page=page, page_size=page_size)
        print("The response of WorkspacesV1Api->get_workspaces:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesV1Api->get_workspaces: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | [**WorkspaceSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **name** | **str**| Search term to filter workspaces by name. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListWorkspace**](ResourceListWorkspace.md)

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

# **patch_workspace**
> Workspace patch_workspace(workspace_id, patch_workspace)

Patch Workspace.

Requires workspace_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.patch_workspace import PatchWorkspace
from arthur_client.api_bindings.models.workspace import Workspace
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
    api_instance = arthur_client.api_bindings.WorkspacesV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    patch_workspace = arthur_client.api_bindings.PatchWorkspace() # PatchWorkspace | 

    try:
        # Patch Workspace.
        api_response = api_instance.patch_workspace(workspace_id, patch_workspace)
        print("The response of WorkspacesV1Api->patch_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesV1Api->patch_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **patch_workspace** | [**PatchWorkspace**](PatchWorkspace.md)|  | 

### Return type

[**Workspace**](Workspace.md)

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

# **post_workspace**
> Workspace post_workspace(post_workspace)

Post Workspace.

Requires organization_create_workspace permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_workspace import PostWorkspace
from arthur_client.api_bindings.models.workspace import Workspace
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
    api_instance = arthur_client.api_bindings.WorkspacesV1Api(api_client)
    post_workspace = arthur_client.api_bindings.PostWorkspace() # PostWorkspace | 

    try:
        # Post Workspace.
        api_response = api_instance.post_workspace(post_workspace)
        print("The response of WorkspacesV1Api->post_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesV1Api->post_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_workspace** | [**PostWorkspace**](PostWorkspace.md)|  | 

### Return type

[**Workspace**](Workspace.md)

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

