# arthur_client.api_bindings.WebhooksV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_webhook**](WebhooksV1Api.md#delete_webhook) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook.
[**get_webhook**](WebhooksV1Api.md#get_webhook) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook.
[**get_workspace_webhooks**](WebhooksV1Api.md#get_workspace_webhooks) | **GET** /api/v1/workspaces/{workspace_id}/webhooks | Get Webhooks.
[**patch_webhook**](WebhooksV1Api.md#patch_webhook) | **PATCH** /api/v1/webhooks/{webhook_id} | Patch Webhook.
[**post_test_webhook**](WebhooksV1Api.md#post_test_webhook) | **POST** /api/v1/workspaces/{workspace_id}/webhooks/test | Post Test Webhook.
[**post_webhook**](WebhooksV1Api.md#post_webhook) | **POST** /api/v1/workspaces/{workspace_id}/webhooks | Post Webhook.


# **delete_webhook**
> delete_webhook(webhook_id)

Delete Webhook.

Requires webhook_delete permission.

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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    webhook_id = 'webhook_id_example' # str | 

    try:
        # Delete Webhook.
        api_instance.delete_webhook(webhook_id)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->delete_webhook: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  | 

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

# **get_webhook**
> Webhook get_webhook(webhook_id)

Get Webhook.

Requires webhook_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.webhook import Webhook
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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    webhook_id = 'webhook_id_example' # str | 

    try:
        # Get Webhook.
        api_response = api_instance.get_webhook(webhook_id)
        print("The response of WebhooksV1Api->get_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->get_webhook: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  | 

### Return type

[**Webhook**](Webhook.md)

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

# **get_workspace_webhooks**
> ResourceListWebhook get_workspace_webhooks(workspace_id, sort=sort, order=order, name=name, page=page, page_size=page_size)

Get Webhooks.

Return a list of webhooks associated with a workspace. Requires workspace_list_webhooks permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_webhook import ResourceListWebhook
from arthur_client.api_bindings.models.sort_order import SortOrder
from arthur_client.api_bindings.models.webhook_sort import WebhookSort
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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    sort = arthur_client.api_bindings.WebhookSort() # WebhookSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    name = 'name_example' # str | Search term to filter webhooks by name. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Webhooks.
        api_response = api_instance.get_workspace_webhooks(workspace_id, sort=sort, order=order, name=name, page=page, page_size=page_size)
        print("The response of WebhooksV1Api->get_workspace_webhooks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->get_workspace_webhooks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **sort** | [**WebhookSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **name** | **str**| Search term to filter webhooks by name. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListWebhook**](ResourceListWebhook.md)

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

# **patch_webhook**
> Webhook patch_webhook(webhook_id, patch_webhook)

Patch Webhook.

Requires webhook_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.patch_webhook import PatchWebhook
from arthur_client.api_bindings.models.webhook import Webhook
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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    webhook_id = 'webhook_id_example' # str | 
    patch_webhook = arthur_client.api_bindings.PatchWebhook() # PatchWebhook | 

    try:
        # Patch Webhook.
        api_response = api_instance.patch_webhook(webhook_id, patch_webhook)
        print("The response of WebhooksV1Api->patch_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->patch_webhook: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  | 
 **patch_webhook** | [**PatchWebhook**](PatchWebhook.md)|  | 

### Return type

[**Webhook**](Webhook.md)

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

# **post_test_webhook**
> WebhookResult post_test_webhook(workspace_id, post_webhook)

Post Test Webhook.

Tests a webhook in a given workspace. Requires workspace_test_webhook permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_webhook import PostWebhook
from arthur_client.api_bindings.models.webhook_result import WebhookResult
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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_webhook = arthur_client.api_bindings.PostWebhook() # PostWebhook | 

    try:
        # Post Test Webhook.
        api_response = api_instance.post_test_webhook(workspace_id, post_webhook)
        print("The response of WebhooksV1Api->post_test_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->post_test_webhook: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_webhook** | [**PostWebhook**](PostWebhook.md)|  | 

### Return type

[**WebhookResult**](WebhookResult.md)

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

# **post_webhook**
> Webhook post_webhook(workspace_id, post_webhook)

Post Webhook.

Creates a webhook in a given workspace. Requires workspace_create_webhook permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.post_webhook import PostWebhook
from arthur_client.api_bindings.models.webhook import Webhook
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
    api_instance = arthur_client.api_bindings.WebhooksV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    post_webhook = arthur_client.api_bindings.PostWebhook() # PostWebhook | 

    try:
        # Post Webhook.
        api_response = api_instance.post_webhook(workspace_id, post_webhook)
        print("The response of WebhooksV1Api->post_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksV1Api->post_webhook: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **post_webhook** | [**PostWebhook**](PostWebhook.md)|  | 

### Return type

[**Webhook**](Webhook.md)

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

