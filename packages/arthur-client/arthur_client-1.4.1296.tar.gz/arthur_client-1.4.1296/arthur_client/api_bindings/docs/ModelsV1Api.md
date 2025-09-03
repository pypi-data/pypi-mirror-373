# arthur_client.api_bindings.ModelsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_model**](ModelsV1Api.md#delete_model) | **DELETE** /api/v1/models/{model_id} | Delete Model By Id
[**delete_model_metrics_schedule**](ModelsV1Api.md#delete_model_metrics_schedule) | **DELETE** /api/v1/models/{model_id}/schedule | Delete Model Metrics Schedule
[**generate_metrics_spec**](ModelsV1Api.md#generate_metrics_spec) | **POST** /api/v1/projects/{project_id}/generate_metrics_spec | Generates A Metrics Spec.
[**get_model**](ModelsV1Api.md#get_model) | **GET** /api/v1/models/{model_id} | Get Model By Id
[**get_models**](ModelsV1Api.md#get_models) | **GET** /api/v1/projects/{project_id}/models | List Models
[**patch_model**](ModelsV1Api.md#patch_model) | **PATCH** /api/v1/models/{model_id} | Update Model
[**post_model**](ModelsV1Api.md#post_model) | **POST** /api/v1/projects/{project_id}/models | Create Model
[**put_model_metric_config**](ModelsV1Api.md#put_model_metric_config) | **PUT** /api/v1/models/{model_id}/metric_config | Update Model Metric Configuration By Model Id
[**put_model_metrics_schedule**](ModelsV1Api.md#put_model_metrics_schedule) | **PUT** /api/v1/models/{model_id}/schedule | Update Model Metrics Schedule


# **delete_model**
> delete_model(model_id)

Delete Model By Id

Deletes a single model. Requires model_delete permission.

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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Delete Model By Id
        api_instance.delete_model(model_id)
    except Exception as e:
        print("Exception when calling ModelsV1Api->delete_model: %s\n" % e)
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
**204** | No Content |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_model_metrics_schedule**
> delete_model_metrics_schedule(model_id)

Delete Model Metrics Schedule

Deletes metrics job schedule. Requires model_metrics_schedule_delete permission.

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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Delete Model Metrics Schedule
        api_instance.delete_model_metrics_schedule(model_id)
    except Exception as e:
        print("Exception when calling ModelsV1Api->delete_model_metrics_schedule: %s\n" % e)
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

# **generate_metrics_spec**
> PutModelMetricSpec generate_metrics_spec(project_id, generate_metrics_spec_request)

Generates A Metrics Spec.

Generates a metric spec for a model based on one or several datasets. Requires project_generate_metrics_spec permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.generate_metrics_spec_request import GenerateMetricsSpecRequest
from arthur_client.api_bindings.models.put_model_metric_spec import PutModelMetricSpec
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    generate_metrics_spec_request = arthur_client.api_bindings.GenerateMetricsSpecRequest() # GenerateMetricsSpecRequest | 

    try:
        # Generates A Metrics Spec.
        api_response = api_instance.generate_metrics_spec(project_id, generate_metrics_spec_request)
        print("The response of ModelsV1Api->generate_metrics_spec:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->generate_metrics_spec: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **generate_metrics_spec_request** | [**GenerateMetricsSpecRequest**](GenerateMetricsSpecRequest.md)|  | 

### Return type

[**PutModelMetricSpec**](PutModelMetricSpec.md)

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

# **get_model**
> Model get_model(model_id)

Get Model By Id

Returns a single model by ID. Requires model_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.model import Model
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # Get Model By Id
        api_response = api_instance.get_model(model_id)
        print("The response of ModelsV1Api->get_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->get_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**Model**](Model.md)

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

# **get_models**
> ResourceListModel get_models(project_id, sort=sort, order=order, dataset_id=dataset_id, name=name, onboarding_identifier=onboarding_identifier, page=page, page_size=page_size)

List Models

Returns models matching the filter and sorting criteria. If multiple filters are specified, results will only be returned that match all of the specified criteria. Requires project_list_models permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.models_sort import ModelsSort
from arthur_client.api_bindings.models.resource_list_model import ResourceListModel
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    sort = arthur_client.api_bindings.ModelsSort() # ModelsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    dataset_id = 'dataset_id_example' # str | Filter the results for the models that are based on this dataset id. Optional. (optional)
    name = 'name_example' # str | Filter the results for the models with a name similar to this name. Optional. (optional)
    onboarding_identifier = 'onboarding_identifier_example' # str | Filter the results for models whose 'onboarding_identifier' matches the provided string. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Models
        api_response = api_instance.get_models(project_id, sort=sort, order=order, dataset_id=dataset_id, name=name, onboarding_identifier=onboarding_identifier, page=page, page_size=page_size)
        print("The response of ModelsV1Api->get_models:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->get_models: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sort** | [**ModelsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **dataset_id** | **str**| Filter the results for the models that are based on this dataset id. Optional. | [optional] 
 **name** | **str**| Filter the results for the models with a name similar to this name. Optional. | [optional] 
 **onboarding_identifier** | **str**| Filter the results for models whose &#39;onboarding_identifier&#39; matches the provided string. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListModel**](ResourceListModel.md)

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

# **patch_model**
> Model patch_model(model_id, patch_model)

Update Model

Updates a single model. Requires model_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.model import Model
from arthur_client.api_bindings.models.patch_model import PatchModel
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    patch_model = arthur_client.api_bindings.PatchModel() # PatchModel | 

    try:
        # Update Model
        api_response = api_instance.patch_model(model_id, patch_model)
        print("The response of ModelsV1Api->patch_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->patch_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **patch_model** | [**PatchModel**](PatchModel.md)|  | 

### Return type

[**Model**](Model.md)

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

# **post_model**
> Model post_model(project_id, post_model)

Create Model

Creates a single model. Requires project_create_model permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.model import Model
from arthur_client.api_bindings.models.post_model import PostModel
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_model = arthur_client.api_bindings.PostModel() # PostModel | 

    try:
        # Create Model
        api_response = api_instance.post_model(project_id, post_model)
        print("The response of ModelsV1Api->post_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->post_model: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_model** | [**PostModel**](PostModel.md)|  | 

### Return type

[**Model**](Model.md)

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

# **put_model_metric_config**
> put_model_metric_config(model_id, put_model_metric_spec)

Update Model Metric Configuration By Model Id

Returns a single model metric spec. Requires model_put_metric_config permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_model_metric_spec import PutModelMetricSpec
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    put_model_metric_spec = arthur_client.api_bindings.PutModelMetricSpec() # PutModelMetricSpec | 

    try:
        # Update Model Metric Configuration By Model Id
        api_instance.put_model_metric_config(model_id, put_model_metric_spec)
    except Exception as e:
        print("Exception when calling ModelsV1Api->put_model_metric_config: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **put_model_metric_spec** | [**PutModelMetricSpec**](PutModelMetricSpec.md)|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_model_metrics_schedule**
> Model put_model_metrics_schedule(model_id, put_model_metrics_schedule)

Update Model Metrics Schedule

Creates or overwrites the model metrics job schedule. Requires model_metrics_schedule_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.model import Model
from arthur_client.api_bindings.models.put_model_metrics_schedule import PutModelMetricsSchedule
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
    api_instance = arthur_client.api_bindings.ModelsV1Api(api_client)
    model_id = 'model_id_example' # str | 
    put_model_metrics_schedule = arthur_client.api_bindings.PutModelMetricsSchedule() # PutModelMetricsSchedule | 

    try:
        # Update Model Metrics Schedule
        api_response = api_instance.put_model_metrics_schedule(model_id, put_model_metrics_schedule)
        print("The response of ModelsV1Api->put_model_metrics_schedule:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsV1Api->put_model_metrics_schedule: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 
 **put_model_metrics_schedule** | [**PutModelMetricsSchedule**](PutModelMetricsSchedule.md)|  | 

### Return type

[**Model**](Model.md)

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

