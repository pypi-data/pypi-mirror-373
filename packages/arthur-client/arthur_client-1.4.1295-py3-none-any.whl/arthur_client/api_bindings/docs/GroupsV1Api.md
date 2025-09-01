# arthur_client.api_bindings.GroupsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assign_users_to_group**](GroupsV1Api.md#assign_users_to_group) | **POST** /api/v1/groups/{group_id}/users | Assign User To Group
[**delete_group**](GroupsV1Api.md#delete_group) | **DELETE** /api/v1/groups/{group_id} | Delete Group
[**get_group**](GroupsV1Api.md#get_group) | **GET** /api/v1/groups/{group_id} | Get Group
[**get_group_users**](GroupsV1Api.md#get_group_users) | **GET** /api/v1/groups/{group_id}/users | Get Group Users
[**get_groups**](GroupsV1Api.md#get_groups) | **GET** /api/v1/organization/groups | List Groups
[**patch_group**](GroupsV1Api.md#patch_group) | **PATCH** /api/v1/groups/{group_id} | Update Group
[**post_group**](GroupsV1Api.md#post_group) | **POST** /api/v1/organization/groups | Create Group
[**remove_users_from_group**](GroupsV1Api.md#remove_users_from_group) | **DELETE** /api/v1/groups/{group_id}/users | Remove Users From Group In Bulk
[**search_group_memberships**](GroupsV1Api.md#search_group_memberships) | **GET** /api/v1/organization/group_memberships | Search Group Memberships


# **assign_users_to_group**
> Group assign_users_to_group(group_id, post_group_membership)

Assign User To Group

Assign user to group by group ID. Requires group_create_group_membership permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.group import Group
from arthur_client.api_bindings.models.post_group_membership import PostGroupMembership
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 
    post_group_membership = arthur_client.api_bindings.PostGroupMembership() # PostGroupMembership | 

    try:
        # Assign User To Group
        api_response = api_instance.assign_users_to_group(group_id, post_group_membership)
        print("The response of GroupsV1Api->assign_users_to_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->assign_users_to_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **post_group_membership** | [**PostGroupMembership**](PostGroupMembership.md)|  | 

### Return type

[**Group**](Group.md)

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

# **delete_group**
> delete_group(group_id)

Delete Group

Deletes group by ID. Requires group_delete permission.

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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 

    try:
        # Delete Group
        api_instance.delete_group(group_id)
    except Exception as e:
        print("Exception when calling GroupsV1Api->delete_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 

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
**204** | Group deleted. |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group**
> Group get_group(group_id)

Get Group

Fetches group by ID. Requires group_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.group import Group
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 

    try:
        # Get Group
        api_response = api_instance.get_group(group_id)
        print("The response of GroupsV1Api->get_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->get_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 

### Return type

[**Group**](Group.md)

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

# **get_group_users**
> ResourceListUser get_group_users(group_id, sort=sort, order=order, search=search, page=page, page_size=page_size)

Get Group Users

Fetches group users by group ID. Requires group_list_users permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_user import ResourceListUser
from arthur_client.api_bindings.models.sort_order import SortOrder
from arthur_client.api_bindings.models.user_sort import UserSort
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 
    sort = arthur_client.api_bindings.UserSort() # UserSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    search = 'search_example' # str | Search for users by name or email. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Group Users
        api_response = api_instance.get_group_users(group_id, sort=sort, order=order, search=search, page=page, page_size=page_size)
        print("The response of GroupsV1Api->get_group_users:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->get_group_users: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **sort** | [**UserSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **search** | **str**| Search for users by name or email. | [optional] 
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

# **get_groups**
> ResourceListGroup get_groups(sort=sort, order=order, name=name, page=page, page_size=page_size)

List Groups

Fetches all groups. Requires organization_list_groups permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.group_sort import GroupSort
from arthur_client.api_bindings.models.resource_list_group import ResourceListGroup
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    sort = arthur_client.api_bindings.GroupSort() # GroupSort | Override the field used for sorting. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order of the returned list. Optional. (optional)
    name = 'name_example' # str | Filter the list of groups by name. Optional. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Groups
        api_response = api_instance.get_groups(sort=sort, order=order, name=name, page=page, page_size=page_size)
        print("The response of GroupsV1Api->get_groups:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->get_groups: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort** | [**GroupSort**](.md)| Override the field used for sorting. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order of the returned list. Optional. | [optional] 
 **name** | **str**| Filter the list of groups by name. Optional. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListGroup**](ResourceListGroup.md)

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

# **patch_group**
> Group patch_group(group_id, patch_group)

Update Group

Updates group by ID. Requires group_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.group import Group
from arthur_client.api_bindings.models.patch_group import PatchGroup
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 
    patch_group = arthur_client.api_bindings.PatchGroup() # PatchGroup | 

    try:
        # Update Group
        api_response = api_instance.patch_group(group_id, patch_group)
        print("The response of GroupsV1Api->patch_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->patch_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **patch_group** | [**PatchGroup**](PatchGroup.md)|  | 

### Return type

[**Group**](Group.md)

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

# **post_group**
> Group post_group(post_group)

Create Group

Requires organization_create_group permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.group import Group
from arthur_client.api_bindings.models.post_group import PostGroup
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    post_group = arthur_client.api_bindings.PostGroup() # PostGroup | 

    try:
        # Create Group
        api_response = api_instance.post_group(post_group)
        print("The response of GroupsV1Api->post_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->post_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_group** | [**PostGroup**](PostGroup.md)|  | 

### Return type

[**Group**](Group.md)

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

# **remove_users_from_group**
> Group remove_users_from_group(group_id, delete_group_membership)

Remove Users From Group In Bulk

Remove all users from group by group ID. Requires group_delete_group_membership permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.delete_group_membership import DeleteGroupMembership
from arthur_client.api_bindings.models.group import Group
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    group_id = 'group_id_example' # str | 
    delete_group_membership = arthur_client.api_bindings.DeleteGroupMembership() # DeleteGroupMembership | 

    try:
        # Remove Users From Group In Bulk
        api_response = api_instance.remove_users_from_group(group_id, delete_group_membership)
        print("The response of GroupsV1Api->remove_users_from_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->remove_users_from_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **delete_group_membership** | [**DeleteGroupMembership**](DeleteGroupMembership.md)|  | 

### Return type

[**Group**](Group.md)

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

# **search_group_memberships**
> ResourceListGroupMembership search_group_memberships(user_ids=user_ids, group_ids=group_ids, group_name=group_name, page=page, page_size=page_size)

Search Group Memberships

Searches memberships for the intersection of user and group IDs. Requires organization_list_group_memberships permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_group_membership import ResourceListGroupMembership
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
    api_instance = arthur_client.api_bindings.GroupsV1Api(api_client)
    user_ids = ['user_ids_example'] # List[Optional[str]] | Filter memberships to select user IDs. (optional)
    group_ids = ['group_ids_example'] # List[Optional[str]] | Filter memberships to select group IDs. (optional)
    group_name = 'group_name_example' # str | Filter memberships by group name. A name matches if it contains the input string case-insensitive. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Search Group Memberships
        api_response = api_instance.search_group_memberships(user_ids=user_ids, group_ids=group_ids, group_name=group_name, page=page, page_size=page_size)
        print("The response of GroupsV1Api->search_group_memberships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GroupsV1Api->search_group_memberships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_ids** | [**List[Optional[str]]**](str.md)| Filter memberships to select user IDs. | [optional] 
 **group_ids** | [**List[Optional[str]]**](str.md)| Filter memberships to select group IDs. | [optional] 
 **group_name** | **str**| Filter memberships by group name. A name matches if it contains the input string case-insensitive. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListGroupMembership**](ResourceListGroupMembership.md)

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

