# arthur_client.api_bindings.AlertsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_alert**](AlertsV1Api.md#get_alert) | **GET** /api/v1/alerts/{alert_id} | Get Alert By Id
[**get_model_alerts**](AlertsV1Api.md#get_model_alerts) | **GET** /api/v1/models/{model_id}/alerts | Get Model Alerts
[**post_model_alerts**](AlertsV1Api.md#post_model_alerts) | **POST** /api/v1/models/{model_id}/alerts | Create Model Alerts


# **get_alert**
> Alert get_alert(alert_id)

Get Alert By Id

Returns a single alert by ID. Requires model_alert_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert import Alert
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
    api_instance = arthur_client.api_bindings.AlertsV1Api(api_client)
    alert_id = 'alert_id_example' # str | 

    try:
        # Get Alert By Id
        api_response = api_instance.get_alert(alert_id)
        print("The response of AlertsV1Api->get_alert:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertsV1Api->get_alert: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_id** | **str**|  | 

### Return type

[**Alert**](Alert.md)

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

# **get_model_alerts**
> InfiniteResourceListAlert get_model_alerts(model_id, sort=sort, order=order, alert_rule_ids=alert_rule_ids, bound=bound, time_from=time_from, time_to=time_to, page=page, page_size=page_size)

Get Model Alerts

Returns a list of alerts associated with a model. Requires model_list_alerts permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_bound import AlertBound
from arthur_client.api_bindings.models.alert_sort import AlertSort
from arthur_client.api_bindings.models.infinite_resource_list_alert import InfiniteResourceListAlert
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
    api_instance = arthur_client.api_bindings.AlertsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    sort = arthur_client.api_bindings.AlertSort() # AlertSort | The field to sort by. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | The order to sort by. (optional)
    alert_rule_ids = ['alert_rule_ids_example'] # List[Optional[str]] | The ID of the alert rule to filter by. (optional)
    bound = arthur_client.api_bindings.AlertBound() # AlertBound | The bound to filter by. (optional)
    time_from = '2013-10-20T19:20:30+01:00' # datetime | The start timestamp to filter by. (optional)
    time_to = '2013-10-20T19:20:30+01:00' # datetime | The end timestamp to filter by. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Model Alerts
        api_response = api_instance.get_model_alerts(model_id, sort=sort, order=order, alert_rule_ids=alert_rule_ids, bound=bound, time_from=time_from, time_to=time_to, page=page, page_size=page_size)
        print("The response of AlertsV1Api->get_model_alerts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertsV1Api->get_model_alerts: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **sort** | [**AlertSort**](.md)| The field to sort by. | [optional] 
 **order** | [**SortOrder**](.md)| The order to sort by. | [optional] 
 **alert_rule_ids** | [**List[Optional[str]]**](str.md)| The ID of the alert rule to filter by. | [optional] 
 **bound** | [**AlertBound**](.md)| The bound to filter by. | [optional] 
 **time_from** | **datetime**| The start timestamp to filter by. | [optional] 
 **time_to** | **datetime**| The end timestamp to filter by. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**InfiniteResourceListAlert**](InfiniteResourceListAlert.md)

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

# **post_model_alerts**
> CreatedAlerts post_model_alerts(model_id, post_alerts)

Create Model Alerts

Creates a list of alerts associated with a model. Requires model_create_alert permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.created_alerts import CreatedAlerts
from arthur_client.api_bindings.models.post_alerts import PostAlerts
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
    api_instance = arthur_client.api_bindings.AlertsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    post_alerts = arthur_client.api_bindings.PostAlerts() # PostAlerts | 

    try:
        # Create Model Alerts
        api_response = api_instance.post_model_alerts(model_id, post_alerts)
        print("The response of AlertsV1Api->post_model_alerts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertsV1Api->post_model_alerts: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **post_alerts** | [**PostAlerts**](PostAlerts.md)|  | 

### Return type

[**CreatedAlerts**](CreatedAlerts.md)

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

