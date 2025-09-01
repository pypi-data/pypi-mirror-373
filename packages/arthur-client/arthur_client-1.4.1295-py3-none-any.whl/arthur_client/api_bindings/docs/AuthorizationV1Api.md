# arthur_client.api_bindings.AuthorizationV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**check_permissions**](AuthorizationV1Api.md#check_permissions) | **POST** /api/v1/permissions/check | Check Permissions
[**delete_role_binding**](AuthorizationV1Api.md#delete_role_binding) | **DELETE** /api/v1/role_bindings/{role_binding_id} | Delete Role Binding.
[**list_group_role_bindings**](AuthorizationV1Api.md#list_group_role_bindings) | **GET** /api/v1/groups/{group_id}/role_bindings | Get Group Role Bindings.
[**list_org_role_bindings**](AuthorizationV1Api.md#list_org_role_bindings) | **GET** /api/v1/organization/role_bindings | List Organization Role Bindings.
[**list_permissions_library**](AuthorizationV1Api.md#list_permissions_library) | **GET** /api/v1/permissions | List Permissions
[**list_project_role_bindings**](AuthorizationV1Api.md#list_project_role_bindings) | **GET** /api/v1/projects/{project_id}/role_bindings | List Project Role Bindings.
[**list_roles**](AuthorizationV1Api.md#list_roles) | **GET** /api/v1/organization/roles | List Roles
[**list_user_role_bindings**](AuthorizationV1Api.md#list_user_role_bindings) | **GET** /api/v1/users/{user_id}/role_bindings | Get User Role Bindings.
[**list_workspace_role_bindings**](AuthorizationV1Api.md#list_workspace_role_bindings) | **GET** /api/v1/workspaces/{workspace_id}/role_bindings | List Workspace Role Bindings.
[**post_org_role_binding**](AuthorizationV1Api.md#post_org_role_binding) | **POST** /api/v1/organization/role_bindings | Post Organization Role Binding.
[**post_project_role_binding**](AuthorizationV1Api.md#post_project_role_binding) | **POST** /api/v1/projects/{project_id}/role_bindings | Post Project Role Binding
[**post_workspace_role_binding**](AuthorizationV1Api.md#post_workspace_role_binding) | **POST** /api/v1/workspaces/{workspace_id}/role_bindings | Post Workspace Role Binding.


# **check_permissions**
> PermissionsResponse check_permissions(permissions_request)

Check Permissions

Check given permissions and returns a list of allowed and not allowed permissions.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.permissions_request import PermissionsRequest
from arthur_client.api_bindings.models.permissions_response import PermissionsResponse
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    permissions_request = arthur_client.api_bindings.PermissionsRequest() # PermissionsRequest | 

    try:
        # Check Permissions
        api_response = api_instance.check_permissions(permissions_request)
        print("The response of AuthorizationV1Api->check_permissions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->check_permissions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permissions_request** | [**PermissionsRequest**](PermissionsRequest.md)|  | 

### Return type

[**PermissionsResponse**](PermissionsResponse.md)

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_role_binding**
> delete_role_binding(role_binding_id)

Delete Role Binding.

Deletes role binding by id. Permission required depends on the role binding type. Deleting an organization role binding requires organization_role_binding_delete permission. Deleting a workspace role binding requires workspace_role_binding_delete permission. Deleting a project role binding requires project_role_binding_delete permission.

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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    role_binding_id = 'role_binding_id_example' # str | 

    try:
        # Delete Role Binding.
        api_instance.delete_role_binding(role_binding_id)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->delete_role_binding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_binding_id** | **str**|  | 

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
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_group_role_bindings**
> ResourceListRoleBinding list_group_role_bindings(group_id, search=search, bound_resource_kind=bound_resource_kind, page=page, page_size=page_size)

Get Group Role Bindings.

Lists all role bindings for the group. Requires group_list_role_bindings permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.bound_resource_kind import BoundResourceKind
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    group_id = 'group_id_example' # str | 
    search = 'search_example' # str | Search for role bindings by workspace name, project name, role name, workspace ID, or project ID. (optional)
    bound_resource_kind = arthur_client.api_bindings.BoundResourceKind() # BoundResourceKind | Filter the list of role bindings by the kind of the bound resource. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Group Role Bindings.
        api_response = api_instance.list_group_role_bindings(group_id, search=search, bound_resource_kind=bound_resource_kind, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_group_role_bindings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_group_role_bindings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **search** | **str**| Search for role bindings by workspace name, project name, role name, workspace ID, or project ID. | [optional] 
 **bound_resource_kind** | [**BoundResourceKind**](.md)| Filter the list of role bindings by the kind of the bound resource. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRoleBinding**](ResourceListRoleBinding.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_org_role_bindings**
> ResourceListRoleBinding list_org_role_bindings(search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)

List Organization Role Bindings.

Fetches all organization role bindings. Requires organization_list_role_bindings permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.bound_member_kind import BoundMemberKind
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding
from arthur_client.api_bindings.models.user_type import UserType
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    search = 'search_example' # str | Search for role bindings by user name, group name, role name, user ID or group ID. (optional)
    bound_member_kind = arthur_client.api_bindings.BoundMemberKind() # BoundMemberKind | Filter the list of role bindings by the kind of the bound member. Optional. (optional)
    user_types = [user, service_account] # List[UserType] | Limits the results to a specific set of user types. Only applies to user role bindings. (optional) (default to [user, service_account])
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Organization Role Bindings.
        api_response = api_instance.list_org_role_bindings(search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_org_role_bindings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_org_role_bindings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search** | **str**| Search for role bindings by user name, group name, role name, user ID or group ID. | [optional] 
 **bound_member_kind** | [**BoundMemberKind**](.md)| Filter the list of role bindings by the kind of the bound member. Optional. | [optional] 
 **user_types** | [**List[UserType]**](UserType.md)| Limits the results to a specific set of user types. Only applies to user role bindings. | [optional] [default to [user, service_account]]
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRoleBinding**](ResourceListRoleBinding.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_permissions_library**
> ResourceListPermission list_permissions_library(search_string=search_string, page=page, page_size=page_size)

List Permissions

Returns list of available permissions.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_permission import ResourceListPermission
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    search_string = 'search_string_example' # str | String to search on. Will perform a substring match of name and description. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Permissions
        api_response = api_instance.list_permissions_library(search_string=search_string, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_permissions_library:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_permissions_library: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_string** | **str**| String to search on. Will perform a substring match of name and description. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListPermission**](ResourceListPermission.md)

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_project_role_bindings**
> ResourceListRoleBinding list_project_role_bindings(project_id, search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)

List Project Role Bindings.

Fetches all project role bindings. Requires project_list_role_bindings permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.bound_member_kind import BoundMemberKind
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding
from arthur_client.api_bindings.models.user_type import UserType
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    project_id = 'project_id_example' # str | 
    search = 'search_example' # str | Search for role bindings by user name, group name, role name, parent workspace name or ID, user ID or group ID. (optional)
    bound_member_kind = arthur_client.api_bindings.BoundMemberKind() # BoundMemberKind | Filter the list of role bindings by the kind of the bound member. Optional. (optional)
    user_types = [user, service_account] # List[UserType] | Limits the results to a specific set of user types. Only applies to user role bindings. (optional) (default to [user, service_account])
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Project Role Bindings.
        api_response = api_instance.list_project_role_bindings(project_id, search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_project_role_bindings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_project_role_bindings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **search** | **str**| Search for role bindings by user name, group name, role name, parent workspace name or ID, user ID or group ID. | [optional] 
 **bound_member_kind** | [**BoundMemberKind**](.md)| Filter the list of role bindings by the kind of the bound member. Optional. | [optional] 
 **user_types** | [**List[UserType]**](UserType.md)| Limits the results to a specific set of user types. Only applies to user role bindings. | [optional] [default to [user, service_account]]
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRoleBinding**](ResourceListRoleBinding.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_roles**
> ResourceListRole list_roles(sort=sort, order=order, name=name, organization_bindable=organization_bindable, workspace_bindable=workspace_bindable, project_bindable=project_bindable, page=page, page_size=page_size)

List Roles

Fetches all roles. Requires organization_list_roles permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_role import ResourceListRole
from arthur_client.api_bindings.models.role_sort import RoleSort
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    sort = arthur_client.api_bindings.RoleSort() # RoleSort | Override the field used for sorting. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order of the returned list. Optional. (optional)
    name = 'name_example' # str | Filter the list of roles by name. Optional. (optional)
    organization_bindable = True # bool | Filter the list of roles by organization bindable. Optional. (optional)
    workspace_bindable = True # bool | Filter the list of roles by workspace bindable. Optional. (optional)
    project_bindable = True # bool | Filter the list of roles by project bindable. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Roles
        api_response = api_instance.list_roles(sort=sort, order=order, name=name, organization_bindable=organization_bindable, workspace_bindable=workspace_bindable, project_bindable=project_bindable, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | [**RoleSort**](.md)| Override the field used for sorting. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order of the returned list. Optional. | [optional] 
 **name** | **str**| Filter the list of roles by name. Optional. | [optional] 
 **organization_bindable** | **bool**| Filter the list of roles by organization bindable. Optional. | [optional] 
 **workspace_bindable** | **bool**| Filter the list of roles by workspace bindable. Optional. | [optional] 
 **project_bindable** | **bool**| Filter the list of roles by project bindable. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRole**](ResourceListRole.md)

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

# **list_user_role_bindings**
> ResourceListRoleBinding list_user_role_bindings(user_id, search=search, bound_resource_kind=bound_resource_kind, page=page, page_size=page_size)

Get User Role Bindings.

Lists all role bindings for the user. Requires user_list_role_bindings permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.bound_resource_kind import BoundResourceKind
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    user_id = 'user_id_example' # str | 
    search = 'search_example' # str | Search for role bindings by workspace name, project name, role name, workspace ID, or project ID. (optional)
    bound_resource_kind = arthur_client.api_bindings.BoundResourceKind() # BoundResourceKind | Filter the list of role bindings by the kind of the bound resource. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get User Role Bindings.
        api_response = api_instance.list_user_role_bindings(user_id, search=search, bound_resource_kind=bound_resource_kind, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_user_role_bindings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_user_role_bindings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **search** | **str**| Search for role bindings by workspace name, project name, role name, workspace ID, or project ID. | [optional] 
 **bound_resource_kind** | [**BoundResourceKind**](.md)| Filter the list of role bindings by the kind of the bound resource. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRoleBinding**](ResourceListRoleBinding.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workspace_role_bindings**
> ResourceListRoleBinding list_workspace_role_bindings(workspace_id, search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)

List Workspace Role Bindings.

Fetches all workspace role bindings. Requires workspace_list_role_bindings permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.bound_member_kind import BoundMemberKind
from arthur_client.api_bindings.models.resource_list_role_binding import ResourceListRoleBinding
from arthur_client.api_bindings.models.user_type import UserType
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    search = 'search_example' # str | Search for role bindings by user name, group name, role name, user ID or group ID. (optional)
    bound_member_kind = arthur_client.api_bindings.BoundMemberKind() # BoundMemberKind | Filter the list of role bindings by the kind of the bound member. Optional. (optional)
    user_types = ["user","service_account"] # List[UserType] | Limits the results to a specific set of user types. Only applies to user role bindings. (optional) (default to ["user","service_account"])
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Workspace Role Bindings.
        api_response = api_instance.list_workspace_role_bindings(workspace_id, search=search, bound_member_kind=bound_member_kind, user_types=user_types, page=page, page_size=page_size)
        print("The response of AuthorizationV1Api->list_workspace_role_bindings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->list_workspace_role_bindings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **search** | **str**| Search for role bindings by user name, group name, role name, user ID or group ID. | [optional] 
 **bound_member_kind** | [**BoundMemberKind**](.md)| Filter the list of role bindings by the kind of the bound member. Optional. | [optional] 
 **user_types** | [**List[UserType]**](UserType.md)| Limits the results to a specific set of user types. Only applies to user role bindings. | [optional] [default to [&quot;user&quot;,&quot;service_account&quot;]]
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListRoleBinding**](ResourceListRoleBinding.md)

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
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_org_role_binding**
> RoleBinding post_org_role_binding(post_role_binding)

Post Organization Role Binding.

Creates new organization role binding. Requires organization_create_role_binding permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_role_binding import PostRoleBinding
from arthur_client.api_bindings.models.role_binding import RoleBinding
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    post_role_binding = arthur_client.api_bindings.PostRoleBinding() # PostRoleBinding | 

    try:
        # Post Organization Role Binding.
        api_response = api_instance.post_org_role_binding(post_role_binding)
        print("The response of AuthorizationV1Api->post_org_role_binding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->post_org_role_binding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_role_binding** | [**PostRoleBinding**](PostRoleBinding.md)|  | 

### Return type

[**RoleBinding**](RoleBinding.md)

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

# **post_project_role_binding**
> RoleBinding post_project_role_binding(project_id, post_role_binding)

Post Project Role Binding

Creates new project role binding. Requires project_create_role_binding permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_role_binding import PostRoleBinding
from arthur_client.api_bindings.models.role_binding import RoleBinding
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_role_binding = arthur_client.api_bindings.PostRoleBinding() # PostRoleBinding | 

    try:
        # Post Project Role Binding
        api_response = api_instance.post_project_role_binding(project_id, post_role_binding)
        print("The response of AuthorizationV1Api->post_project_role_binding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->post_project_role_binding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_role_binding** | [**PostRoleBinding**](PostRoleBinding.md)|  | 

### Return type

[**RoleBinding**](RoleBinding.md)

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

# **post_workspace_role_binding**
> RoleBinding post_workspace_role_binding(workspace_id, post_role_binding)

Post Workspace Role Binding.

Creates new workspace role binding. Requires workspace_create_role_binding permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_role_binding import PostRoleBinding
from arthur_client.api_bindings.models.role_binding import RoleBinding
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
    api_instance = arthur_client.api_bindings.AuthorizationV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_role_binding = arthur_client.api_bindings.PostRoleBinding() # PostRoleBinding | 

    try:
        # Post Workspace Role Binding.
        api_response = api_instance.post_workspace_role_binding(workspace_id, post_role_binding)
        print("The response of AuthorizationV1Api->post_workspace_role_binding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationV1Api->post_workspace_role_binding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_role_binding** | [**PostRoleBinding**](PostRoleBinding.md)|  | 

### Return type

[**RoleBinding**](RoleBinding.md)

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

