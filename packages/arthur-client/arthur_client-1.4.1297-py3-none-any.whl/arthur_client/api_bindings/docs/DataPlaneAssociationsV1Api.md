# arthur_client.api_bindings.DataPlaneAssociationsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_data_plane_association**](DataPlaneAssociationsV1Api.md#delete_data_plane_association) | **DELETE** /api/v1/data_plane_associations/{data_plane_association_id} | Delete Data Plane Association By Id
[**get_data_plane_project_associations**](DataPlaneAssociationsV1Api.md#get_data_plane_project_associations) | **GET** /api/v1/data_planes/{data_plane_id}/associations | List Projects Associated With The Data Plane
[**get_project_data_plane_associations**](DataPlaneAssociationsV1Api.md#get_project_data_plane_associations) | **GET** /api/v1/projects/{project_id}/data_plane_associations | List Data Plane Associations For Project.
[**get_workspace_data_plane_associations**](DataPlaneAssociationsV1Api.md#get_workspace_data_plane_associations) | **GET** /api/v1/workspaces/{workspace_id}/data_plane_associations | List Data Plane Associations For Workspace.
[**post_data_plane_association**](DataPlaneAssociationsV1Api.md#post_data_plane_association) | **POST** /api/v1/workspaces/{workspace_id}/data_plane_associations | Post Data Plane Association.


# **delete_data_plane_association**
> delete_data_plane_association(data_plane_association_id)

Delete Data Plane Association By Id

Deletes a single data plane association. Requires data_plane_association_delete permission.

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
    api_instance = arthur_client.api_bindings.DataPlaneAssociationsV1Api(api_client)
    data_plane_association_id = 'data_plane_association_id_example' # str | 

    try:
        # Delete Data Plane Association By Id
        api_instance.delete_data_plane_association(data_plane_association_id)
    except Exception as e:
        print("Exception when calling DataPlaneAssociationsV1Api->delete_data_plane_association: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_association_id** | **str**|  | 

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

# **get_data_plane_project_associations**
> ResourceListDataPlaneAssociation get_data_plane_project_associations(data_plane_id, sort=sort, order=order, page=page, page_size=page_size)

List Projects Associated With The Data Plane

Requires data_plane_list_associations permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane_association_sort import DataPlaneAssociationSort
from arthur_client.api_bindings.models.resource_list_data_plane_association import ResourceListDataPlaneAssociation
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
    api_instance = arthur_client.api_bindings.DataPlaneAssociationsV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 
    sort = arthur_client.api_bindings.DataPlaneAssociationSort() # DataPlaneAssociationSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Projects Associated With The Data Plane
        api_response = api_instance.get_data_plane_project_associations(data_plane_id, sort=sort, order=order, page=page, page_size=page_size)
        print("The response of DataPlaneAssociationsV1Api->get_data_plane_project_associations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlaneAssociationsV1Api->get_data_plane_project_associations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 
 **sort** | [**DataPlaneAssociationSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataPlaneAssociation**](ResourceListDataPlaneAssociation.md)

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

# **get_project_data_plane_associations**
> ResourceListDataPlaneAssociation get_project_data_plane_associations(project_id, sort=sort, order=order, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)

List Data Plane Associations For Project.

Requires project_list_data_plane_associations.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane_association_sort import DataPlaneAssociationSort
from arthur_client.api_bindings.models.resource_list_data_plane_association import ResourceListDataPlaneAssociation
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
    api_instance = arthur_client.api_bindings.DataPlaneAssociationsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    sort = arthur_client.api_bindings.DataPlaneAssociationSort() # DataPlaneAssociationSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    gen_ai_enabled = True # bool | Filter to only return engines enabled with the GenAI capability (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Data Plane Associations For Project.
        api_response = api_instance.get_project_data_plane_associations(project_id, sort=sort, order=order, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)
        print("The response of DataPlaneAssociationsV1Api->get_project_data_plane_associations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlaneAssociationsV1Api->get_project_data_plane_associations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sort** | [**DataPlaneAssociationSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **gen_ai_enabled** | **bool**| Filter to only return engines enabled with the GenAI capability | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataPlaneAssociation**](ResourceListDataPlaneAssociation.md)

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

# **get_workspace_data_plane_associations**
> ResourceListDataPlaneAssociation get_workspace_data_plane_associations(workspace_id, sort=sort, order=order, include_projects=include_projects, include_data_planes=include_data_planes, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)

List Data Plane Associations For Workspace.

Requires workspace_list_data_plane_associations permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane_association_sort import DataPlaneAssociationSort
from arthur_client.api_bindings.models.resource_list_data_plane_association import ResourceListDataPlaneAssociation
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
    api_instance = arthur_client.api_bindings.DataPlaneAssociationsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    sort = arthur_client.api_bindings.DataPlaneAssociationSort() # DataPlaneAssociationSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    include_projects = False # bool | Include project details in the response. Defaults to false. (optional) (default to False)
    include_data_planes = False # bool | Include data plane details in the response. Defaults to false. (optional) (default to False)
    gen_ai_enabled = True # bool | Filter to only return engines enabled with the GenAI capability (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Data Plane Associations For Workspace.
        api_response = api_instance.get_workspace_data_plane_associations(workspace_id, sort=sort, order=order, include_projects=include_projects, include_data_planes=include_data_planes, gen_ai_enabled=gen_ai_enabled, page=page, page_size=page_size)
        print("The response of DataPlaneAssociationsV1Api->get_workspace_data_plane_associations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlaneAssociationsV1Api->get_workspace_data_plane_associations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **sort** | [**DataPlaneAssociationSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **include_projects** | **bool**| Include project details in the response. Defaults to false. | [optional] [default to False]
 **include_data_planes** | **bool**| Include data plane details in the response. Defaults to false. | [optional] [default to False]
 **gen_ai_enabled** | **bool**| Filter to only return engines enabled with the GenAI capability | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataPlaneAssociation**](ResourceListDataPlaneAssociation.md)

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

# **post_data_plane_association**
> DataPlaneAssociation post_data_plane_association(workspace_id, post_data_plane_association)

Post Data Plane Association.

Requires workspace_create_data_plane_association permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_plane_association import DataPlaneAssociation
from arthur_client.api_bindings.models.post_data_plane_association import PostDataPlaneAssociation
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
    api_instance = arthur_client.api_bindings.DataPlaneAssociationsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_data_plane_association = arthur_client.api_bindings.PostDataPlaneAssociation() # PostDataPlaneAssociation | 

    try:
        # Post Data Plane Association.
        api_response = api_instance.post_data_plane_association(workspace_id, post_data_plane_association)
        print("The response of DataPlaneAssociationsV1Api->post_data_plane_association:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataPlaneAssociationsV1Api->post_data_plane_association: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_data_plane_association** | [**PostDataPlaneAssociation**](PostDataPlaneAssociation.md)|  | 

### Return type

[**DataPlaneAssociation**](DataPlaneAssociation.md)

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

