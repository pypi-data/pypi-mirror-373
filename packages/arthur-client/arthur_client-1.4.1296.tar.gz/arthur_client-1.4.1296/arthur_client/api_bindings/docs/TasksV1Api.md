# arthur_client.api_bindings.TasksV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_connection_info**](TasksV1Api.md#delete_connection_info) | **DELETE** /api/v1/models/{model_id}/task/connection_info | Delete Connection Info.
[**delete_task**](TasksV1Api.md#delete_task) | **DELETE** /api/v1/models/{model_id}/task | Delete A Task
[**get_task_connection_info**](TasksV1Api.md#get_task_connection_info) | **GET** /api/v1/models/{model_id}/task/connection_info | Get Task Connection Info
[**get_task_state_cache**](TasksV1Api.md#get_task_state_cache) | **GET** /api/v1/models/{model_id}/task | Get Cached Task State
[**patch_task**](TasksV1Api.md#patch_task) | **PATCH** /api/v1/models/{model_id}/task | Update A Task
[**post_regenerate_validation_key**](TasksV1Api.md#post_regenerate_validation_key) | **POST** /api/v1/models/{model_id}/task/regenerate_validation_key | Regenerate Task Validation Key
[**project_create_model_link_task**](TasksV1Api.md#project_create_model_link_task) | **POST** /api/v1/projects/{project_id}/link_task | Link An Existing Task To A New Model.
[**project_create_model_task**](TasksV1Api.md#project_create_model_task) | **POST** /api/v1/projects/{project_id}/tasks | Create A Task.
[**put_task_connection_info**](TasksV1Api.md#put_task_connection_info) | **PUT** /api/v1/models/{model_id}/task/connection_info | Upload Task State
[**put_task_state_cache**](TasksV1Api.md#put_task_state_cache) | **PUT** /api/v1/models/{model_id}/task/cache | Upload Task State
[**sync_task**](TasksV1Api.md#sync_task) | **POST** /api/v1/models/{model_id}/task/sync | Sync A Task


# **delete_connection_info**
> delete_connection_info(model_id)

Delete Connection Info.

Deletes connection information for a model. Requires model_task_delete_connection_info permission.

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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Delete Connection Info.
        api_instance.delete_connection_info(model_id)
    except Exception as e:
        print("Exception when calling TasksV1Api->delete_connection_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

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

# **delete_task**
> TaskMutationResponse delete_task(model_id)

Delete A Task

Submits a job to delete the task and the corresponding platform model, and returns the job ID. Requires model_task_delete permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Delete A Task
        api_response = api_instance.delete_task(model_id)
        print("The response of TasksV1Api->delete_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->delete_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**TaskMutationResponse**](TaskMutationResponse.md)

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

# **get_task_connection_info**
> TaskConnectionInfo get_task_connection_info(model_id)

Get Task Connection Info

Retrieve the task connection information. Requires model_task_get_connection_info permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.task_connection_info import TaskConnectionInfo
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Get Task Connection Info
        api_response = api_instance.get_task_connection_info(model_id)
        print("The response of TasksV1Api->get_task_connection_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->get_task_connection_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**TaskConnectionInfo**](TaskConnectionInfo.md)

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

# **get_task_state_cache**
> TaskReadResponse get_task_state_cache(model_id)

Get Cached Task State

Retrieve the task state cached in the control plane. Requires model_task_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.task_read_response import TaskReadResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Get Cached Task State
        api_response = api_instance.get_task_state_cache(model_id)
        print("The response of TasksV1Api->get_task_state_cache:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->get_task_state_cache: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**TaskReadResponse**](TaskReadResponse.md)

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

# **patch_task**
> TaskMutationResponse patch_task(model_id, patch_task_request)

Update A Task

Submits a job to update the task definition for this model and returns the job ID. When the job finishes, it will upload the latest copy of the task state. Requires model_task_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.patch_task_request import PatchTaskRequest
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 
    patch_task_request = arthur_client.api_bindings.PatchTaskRequest() # PatchTaskRequest | 

    try:
        # Update A Task
        api_response = api_instance.patch_task(model_id, patch_task_request)
        print("The response of TasksV1Api->patch_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->patch_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **patch_task_request** | [**PatchTaskRequest**](PatchTaskRequest.md)|  | 

### Return type

[**TaskMutationResponse**](TaskMutationResponse.md)

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

# **post_regenerate_validation_key**
> TaskValidationKeyRegenerationResponse post_regenerate_validation_key(model_id)

Regenerate Task Validation Key

Regenerate the task validation key. Requires model_task_regenerate_validation_key permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.task_validation_key_regeneration_response import TaskValidationKeyRegenerationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Regenerate Task Validation Key
        api_response = api_instance.post_regenerate_validation_key(model_id)
        print("The response of TasksV1Api->post_regenerate_validation_key:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->post_regenerate_validation_key: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**TaskValidationKeyRegenerationResponse**](TaskValidationKeyRegenerationResponse.md)

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

# **project_create_model_link_task**
> TaskMutationResponse project_create_model_link_task(project_id, post_link_task_request)

Link An Existing Task To A New Model.

Submits a job to link an existing task to a new model in the project and returns a job ID. When the job finishes, it will upload a copy of the task state. Requires the project_create_model_link_task permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_link_task_request import PostLinkTaskRequest
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_link_task_request = arthur_client.api_bindings.PostLinkTaskRequest() # PostLinkTaskRequest | 

    try:
        # Link An Existing Task To A New Model.
        api_response = api_instance.project_create_model_link_task(project_id, post_link_task_request)
        print("The response of TasksV1Api->project_create_model_link_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->project_create_model_link_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_link_task_request** | [**PostLinkTaskRequest**](PostLinkTaskRequest.md)|  | 

### Return type

[**TaskMutationResponse**](TaskMutationResponse.md)

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

# **project_create_model_task**
> TaskMutationResponse project_create_model_task(project_id, post_task_request)

Create A Task.

Submits a job to create a task in the project and returns a job ID. When the job finishes, it will upload a copy of the task state. Requires the project_create_model_task permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_task_request import PostTaskRequest
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_task_request = arthur_client.api_bindings.PostTaskRequest() # PostTaskRequest | 

    try:
        # Create A Task.
        api_response = api_instance.project_create_model_task(project_id, post_task_request)
        print("The response of TasksV1Api->project_create_model_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->project_create_model_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_task_request** | [**PostTaskRequest**](PostTaskRequest.md)|  | 

### Return type

[**TaskMutationResponse**](TaskMutationResponse.md)

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

# **put_task_connection_info**
> TaskConnectionInfo put_task_connection_info(model_id, put_task_connection_info)

Upload Task State

Upload the task connection information. Requires model_task_put_connection_info permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_task_connection_info import PutTaskConnectionInfo
from arthur_client.api_bindings.models.task_connection_info import TaskConnectionInfo
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 
    put_task_connection_info = arthur_client.api_bindings.PutTaskConnectionInfo() # PutTaskConnectionInfo | 

    try:
        # Upload Task State
        api_response = api_instance.put_task_connection_info(model_id, put_task_connection_info)
        print("The response of TasksV1Api->put_task_connection_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->put_task_connection_info: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **put_task_connection_info** | [**PutTaskConnectionInfo**](PutTaskConnectionInfo.md)|  | 

### Return type

[**TaskConnectionInfo**](TaskConnectionInfo.md)

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

# **put_task_state_cache**
> put_task_state_cache(model_id, put_task_state_cache_request)

Upload Task State

Upload a copy of the task state to cache in the control plane. Requires model_task_put_state_cache permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_task_state_cache_request import PutTaskStateCacheRequest
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 
    put_task_state_cache_request = arthur_client.api_bindings.PutTaskStateCacheRequest() # PutTaskStateCacheRequest | 

    try:
        # Upload Task State
        api_instance.put_task_state_cache(model_id, put_task_state_cache_request)
    except Exception as e:
        print("Exception when calling TasksV1Api->put_task_state_cache: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **put_task_state_cache_request** | [**PutTaskStateCacheRequest**](PutTaskStateCacheRequest.md)|  | 

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
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sync_task**
> TaskMutationResponse sync_task(model_id)

Sync A Task

Submits a job to fetch the latest task state and returns the job ID. When the job finishes, it will upload the latest copy of the task state. Requires model_task_sync permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.task_mutation_response import TaskMutationResponse
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
    api_instance = arthur_client.api_bindings.TasksV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Sync A Task
        api_response = api_instance.sync_task(model_id)
        print("The response of TasksV1Api->sync_task:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TasksV1Api->sync_task: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**TaskMutationResponse**](TaskMutationResponse.md)

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

