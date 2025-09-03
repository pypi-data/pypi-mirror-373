# arthur_client.api_bindings.UsersV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_my_invites**](UsersV1Api.md#accept_my_invites) | **POST** /api/v1/users/me/accept-invite | Accept User Invitations
[**delete_user**](UsersV1Api.md#delete_user) | **DELETE** /api/v1/users/{user_id} | Delete User
[**get_organization_users**](UsersV1Api.md#get_organization_users) | **GET** /api/v1/organization/users | Get Users In An Organization.
[**get_users_me**](UsersV1Api.md#get_users_me) | **GET** /api/v1/users/me | Get User Metadata
[**patch_service_account_user**](UsersV1Api.md#patch_service_account_user) | **PATCH** /api/v1/users/{user_id}/service_account | Patch Service Account User.
[**patch_user**](UsersV1Api.md#patch_user) | **PATCH** /api/v1/users/{user_id} | Patch User.
[**post_organization_service_account**](UsersV1Api.md#post_organization_service_account) | **POST** /api/v1/organization/service_accounts | Create Service Account
[**post_organization_user**](UsersV1Api.md#post_organization_user) | **POST** /api/v1/organization/users | Create User
[**post_organization_user_invite**](UsersV1Api.md#post_organization_user_invite) | **POST** /api/v1/organization/users/invite-user | Create User Via Email Invite
[**post_user_creds**](UsersV1Api.md#post_user_creds) | **POST** /api/v1/users/{user_id}/credentials | Regenerate User Credentials.


# **accept_my_invites**
> accept_my_invites()

Accept User Invitations

Accepts pending invitations for the user.

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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)

    try:
        # Accept User Invitations
        api_instance.accept_my_invites()
    except Exception as e:
        print("Exception when calling UsersV1Api->accept_my_invites: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_user**
> delete_user(user_id)

Delete User

Requires delete_user permission.

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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    user_id = 'user_id_example' # str | 

    try:
        # Delete User
        api_instance.delete_user(user_id)
    except Exception as e:
        print("Exception when calling UsersV1Api->delete_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 

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

# **get_organization_users**
> ResourceListUser get_organization_users(sort=sort, order=order, user_types=user_types, search=search, user_ids=user_ids, page=page, page_size=page_size)

Get Users In An Organization.

Requires organization_list_users permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_user import ResourceListUser
from arthur_client.api_bindings.models.sort_order import SortOrder
from arthur_client.api_bindings.models.user_sort import UserSort
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    sort = arthur_client.api_bindings.UserSort() # UserSort | Override the field used for sorting. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    user_types = ["user","service_account"] # List[UserType] | Limits the results to a specific set of user types. (optional) (default to ["user","service_account"])
    search = 'search_example' # str | Search for users by name or email. (optional)
    user_ids = ['user_ids_example'] # List[Optional[str]] | Optional list of user IDs to filter down. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Users In An Organization.
        api_response = api_instance.get_organization_users(sort=sort, order=order, user_types=user_types, search=search, user_ids=user_ids, page=page, page_size=page_size)
        print("The response of UsersV1Api->get_organization_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->get_organization_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | [**UserSort**](.md)| Override the field used for sorting. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **user_types** | [**List[UserType]**](UserType.md)| Limits the results to a specific set of user types. | [optional] [default to [&quot;user&quot;,&quot;service_account&quot;]]
 **search** | **str**| Search for users by name or email. | [optional] 
 **user_ids** | [**List[Optional[str]]**](str.md)| Optional list of user IDs to filter down. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListUser**](ResourceListUser.md)

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

# **get_users_me**
> User get_users_me()

Get User Metadata

Returns Arthur user metadata.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.user import User
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)

    try:
        # Get User Metadata
        api_response = api_instance.get_users_me()
        print("The response of UsersV1Api->get_users_me:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->get_users_me: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**User**](User.md)

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_service_account_user**
> User patch_service_account_user(user_id, patch_service_account_user)

Patch Service Account User.

Requires user_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.patch_service_account_user import PatchServiceAccountUser
from arthur_client.api_bindings.models.user import User
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    user_id = 'user_id_example' # str | 
    patch_service_account_user = arthur_client.api_bindings.PatchServiceAccountUser() # PatchServiceAccountUser | 

    try:
        # Patch Service Account User.
        api_response = api_instance.patch_service_account_user(user_id, patch_service_account_user)
        print("The response of UsersV1Api->patch_service_account_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->patch_service_account_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **patch_service_account_user** | [**PatchServiceAccountUser**](PatchServiceAccountUser.md)|  | 

### Return type

[**User**](User.md)

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

# **patch_user**
> User patch_user(user_id, patch_user)

Patch User.

Requires user_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.patch_user import PatchUser
from arthur_client.api_bindings.models.user import User
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    user_id = 'user_id_example' # str | 
    patch_user = arthur_client.api_bindings.PatchUser() # PatchUser | 

    try:
        # Patch User.
        api_response = api_instance.patch_user(user_id, patch_user)
        print("The response of UsersV1Api->patch_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->patch_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **patch_user** | [**PatchUser**](PatchUser.md)|  | 

### Return type

[**User**](User.md)

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

# **post_organization_service_account**
> UserServiceAccountCredentials post_organization_service_account(post_service_account)

Create Service Account

Requires organization_create_service_account permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_service_account import PostServiceAccount
from arthur_client.api_bindings.models.user_service_account_credentials import UserServiceAccountCredentials
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    post_service_account = arthur_client.api_bindings.PostServiceAccount() # PostServiceAccount | 

    try:
        # Create Service Account
        api_response = api_instance.post_organization_service_account(post_service_account)
        print("The response of UsersV1Api->post_organization_service_account:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->post_organization_service_account: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_service_account** | [**PostServiceAccount**](PostServiceAccount.md)|  | 

### Return type

[**UserServiceAccountCredentials**](UserServiceAccountCredentials.md)

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

# **post_organization_user**
> User post_organization_user(post_end_user)

Create User

Requires organization_create_user permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_end_user import PostEndUser
from arthur_client.api_bindings.models.user import User
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    post_end_user = arthur_client.api_bindings.PostEndUser() # PostEndUser | 

    try:
        # Create User
        api_response = api_instance.post_organization_user(post_end_user)
        print("The response of UsersV1Api->post_organization_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->post_organization_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_end_user** | [**PostEndUser**](PostEndUser.md)|  | 

### Return type

[**User**](User.md)

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
**409** | Conflict |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_organization_user_invite**
> object post_organization_user_invite(invite_new_user)

Create User Via Email Invite

Requires organization_invite_user permission. Also requires underlying permissions for managing user permissions: group_create_group_membership, organization_create_role_binding, workspace_create_role_binding, or project_create_role_binding depending on whether the user is being added to a group or granted a role bound to an organization, workspace, or project.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.invite_new_user import InviteNewUser
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    invite_new_user = arthur_client.api_bindings.InviteNewUser() # InviteNewUser | 

    try:
        # Create User Via Email Invite
        api_response = api_instance.post_organization_user_invite(invite_new_user)
        print("The response of UsersV1Api->post_organization_user_invite:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->post_organization_user_invite: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_new_user** | [**InviteNewUser**](InviteNewUser.md)|  | 

### Return type

**object**

### Authorization

[OAuth2AuthorizationCode](../README.md#OAuth2AuthorizationCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_user_creds**
> SensitiveUser post_user_creds(user_id)

Regenerate User Credentials.

Requires user_regenerate_creds permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.sensitive_user import SensitiveUser
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
    api_instance = arthur_client.api_bindings.UsersV1Api(api_client)
    user_id = 'user_id_example' # str | 

    try:
        # Regenerate User Credentials.
        api_response = api_instance.post_user_creds(user_id)
        print("The response of UsersV1Api->post_user_creds:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersV1Api->post_user_creds: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 

### Return type

[**SensitiveUser**](SensitiveUser.md)

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

