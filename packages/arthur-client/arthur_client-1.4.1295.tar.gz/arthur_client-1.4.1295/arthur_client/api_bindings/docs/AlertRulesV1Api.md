# arthur_client.api_bindings.AlertRulesV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_alert_rule**](AlertRulesV1Api.md#delete_alert_rule) | **DELETE** /api/v1/alert_rules/{alert_rule_id} | Delete Alert Rule By Id
[**get_alert_rule**](AlertRulesV1Api.md#get_alert_rule) | **GET** /api/v1/alert_rules/{alert_rule_id} | Get Alert Rule By Id
[**get_model_alert_rules**](AlertRulesV1Api.md#get_model_alert_rules) | **GET** /api/v1/models/{model_id}/alert_rules | Get Model Alert Rules
[**patch_alert_rule**](AlertRulesV1Api.md#patch_alert_rule) | **PATCH** /api/v1/alert_rules/{alert_rule_id} | Update Model Alert Rule
[**post_alert_rule_query_validation**](AlertRulesV1Api.md#post_alert_rule_query_validation) | **POST** /api/v1/models/{model_id}/alert_rule_query_validation | Validate A Model Alert Rule Query
[**post_model_alert_rule**](AlertRulesV1Api.md#post_model_alert_rule) | **POST** /api/v1/models/{model_id}/alert_rules | Create Model Alert Rule


# **delete_alert_rule**
> delete_alert_rule(alert_rule_id)

Delete Alert Rule By Id

Deletes a single alert rule by ID. Requires alert_rule_delete permission.

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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    alert_rule_id = 'alert_rule_id_example' # str | 

    try:
        # Delete Alert Rule By Id
        api_instance.delete_alert_rule(alert_rule_id)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->delete_alert_rule: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_rule_id** | **str**|  | 

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

# **get_alert_rule**
> AlertRule get_alert_rule(alert_rule_id)

Get Alert Rule By Id

Returns a single alert rule by ID. Requires alert_rule_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_rule import AlertRule
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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    alert_rule_id = 'alert_rule_id_example' # str | 

    try:
        # Get Alert Rule By Id
        api_response = api_instance.get_alert_rule(alert_rule_id)
        print("The response of AlertRulesV1Api->get_alert_rule:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->get_alert_rule: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_rule_id** | **str**|  | 

### Return type

[**AlertRule**](AlertRule.md)

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

# **get_model_alert_rules**
> ResourceListAlertRule get_model_alert_rules(model_id, sort=sort, order=order, name=name, bound=bound, query=query, threshold_less_than=threshold_less_than, threshold_greater_than=threshold_greater_than, metric_name=metric_name, page=page, page_size=page_size)

Get Model Alert Rules

Returns a list of alert rules associated with a model. Requires model_list_alert_rules permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_bound import AlertBound
from arthur_client.api_bindings.models.alert_rule_sort import AlertRuleSort
from arthur_client.api_bindings.models.resource_list_alert_rule import ResourceListAlertRule
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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    model_id = 'model_id_example' # str | 
    sort = arthur_client.api_bindings.AlertRuleSort() # AlertRuleSort | The field to sort by. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | The order to sort by. (optional)
    name = 'name_example' # str | The name of the alert rule to search by. (optional)
    bound = arthur_client.api_bindings.AlertBound() # AlertBound | The bound to filter by. (optional)
    query = 'query_example' # str | The query to filter by. (optional)
    threshold_less_than = 3.4 # float | The threshold to filter by, less than. (optional)
    threshold_greater_than = 3.4 # float | The threshold to filter by, greater than. (optional)
    metric_name = 'metric_name_example' # str | The name of the alert rule query metric to search by. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Model Alert Rules
        api_response = api_instance.get_model_alert_rules(model_id, sort=sort, order=order, name=name, bound=bound, query=query, threshold_less_than=threshold_less_than, threshold_greater_than=threshold_greater_than, metric_name=metric_name, page=page, page_size=page_size)
        print("The response of AlertRulesV1Api->get_model_alert_rules:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->get_model_alert_rules: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **sort** | [**AlertRuleSort**](.md)| The field to sort by. | [optional] 
 **order** | [**SortOrder**](.md)| The order to sort by. | [optional] 
 **name** | **str**| The name of the alert rule to search by. | [optional] 
 **bound** | [**AlertBound**](.md)| The bound to filter by. | [optional] 
 **query** | **str**| The query to filter by. | [optional] 
 **threshold_less_than** | **float**| The threshold to filter by, less than. | [optional] 
 **threshold_greater_than** | **float**| The threshold to filter by, greater than. | [optional] 
 **metric_name** | **str**| The name of the alert rule query metric to search by. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListAlertRule**](ResourceListAlertRule.md)

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

# **patch_alert_rule**
> AlertRule patch_alert_rule(alert_rule_id, patch_alert_rule)

Update Model Alert Rule

Updates an alert rule. Requires alert_rule_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_rule import AlertRule
from arthur_client.api_bindings.models.patch_alert_rule import PatchAlertRule
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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    alert_rule_id = 'alert_rule_id_example' # str | 
    patch_alert_rule = arthur_client.api_bindings.PatchAlertRule() # PatchAlertRule | 

    try:
        # Update Model Alert Rule
        api_response = api_instance.patch_alert_rule(alert_rule_id, patch_alert_rule)
        print("The response of AlertRulesV1Api->patch_alert_rule:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->patch_alert_rule: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_rule_id** | **str**|  | 
 **patch_alert_rule** | [**PatchAlertRule**](PatchAlertRule.md)|  | 

### Return type

[**AlertRule**](AlertRule.md)

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

# **post_alert_rule_query_validation**
> AlertRuleSQLValidationResp post_alert_rule_query_validation(model_id, validate_alert_rule_query_req)

Validate A Model Alert Rule Query

Validates an alert rule query. Requires model_create_alert_rule permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_rule_sql_validation_resp import AlertRuleSQLValidationResp
from arthur_client.api_bindings.models.validate_alert_rule_query_req import ValidateAlertRuleQueryReq
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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    model_id = 'model_id_example' # str | 
    validate_alert_rule_query_req = arthur_client.api_bindings.ValidateAlertRuleQueryReq() # ValidateAlertRuleQueryReq | 

    try:
        # Validate A Model Alert Rule Query
        api_response = api_instance.post_alert_rule_query_validation(model_id, validate_alert_rule_query_req)
        print("The response of AlertRulesV1Api->post_alert_rule_query_validation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->post_alert_rule_query_validation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **validate_alert_rule_query_req** | [**ValidateAlertRuleQueryReq**](ValidateAlertRuleQueryReq.md)|  | 

### Return type

[**AlertRuleSQLValidationResp**](AlertRuleSQLValidationResp.md)

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

# **post_model_alert_rule**
> AlertRule post_model_alert_rule(model_id, post_alert_rule)

Create Model Alert Rule

Creates an alert rule. Requires model_create_alert_rule permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.alert_rule import AlertRule
from arthur_client.api_bindings.models.post_alert_rule import PostAlertRule
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
    api_instance = arthur_client.api_bindings.AlertRulesV1Api(api_client)
    model_id = 'model_id_example' # str | 
    post_alert_rule = arthur_client.api_bindings.PostAlertRule() # PostAlertRule | 

    try:
        # Create Model Alert Rule
        api_response = api_instance.post_model_alert_rule(model_id, post_alert_rule)
        print("The response of AlertRulesV1Api->post_model_alert_rule:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlertRulesV1Api->post_model_alert_rule: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **post_alert_rule** | [**PostAlertRule**](PostAlertRule.md)|  | 

### Return type

[**AlertRule**](AlertRule.md)

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

