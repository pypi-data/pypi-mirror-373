# arthur_client.api_bindings.DataRetrievalV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_available_data_retrieval_data**](DataRetrievalV1Api.md#delete_available_data_retrieval_data) | **DELETE** /api/v1/available_dataset/{available_dataset_id}/data_retrieval/{operation_id} | Delete Retrieved Data
[**delete_data_retrieval_data**](DataRetrievalV1Api.md#delete_data_retrieval_data) | **DELETE** /api/v1/datasets/{dataset_id}/data_retrieval/{operation_id} | Delete Retrieved Data
[**get_available_data_retrieval_data**](DataRetrievalV1Api.md#get_available_data_retrieval_data) | **GET** /api/v1/available_dataset/{available_dataset_id}/data_retrieval/{operation_id} | Gets Raw Data Operation Data
[**get_data_retrieval_data**](DataRetrievalV1Api.md#get_data_retrieval_data) | **GET** /api/v1/datasets/{dataset_id}/data_retrieval/{operation_id} | Gets Raw Data Operation Data
[**post_available_data_retrieval_operation**](DataRetrievalV1Api.md#post_available_data_retrieval_operation) | **POST** /api/v1/available_dataset/{available_dataset_id}/data_retrieval | Create Raw Data Operation
[**post_data_retrieval_operation**](DataRetrievalV1Api.md#post_data_retrieval_operation) | **POST** /api/v1/datasets/{dataset_id}/data_retrieval | Create Raw Data Operation
[**put_available_data_retrieval_data**](DataRetrievalV1Api.md#put_available_data_retrieval_data) | **PUT** /api/v1/available_dataset/{available_dataset_id}/data_retrieval/{operation_id} | Put Retrieved Data
[**put_data_retrieval_data**](DataRetrievalV1Api.md#put_data_retrieval_data) | **PUT** /api/v1/datasets/{dataset_id}/data_retrieval/{operation_id} | Put Retrieved Data


# **delete_available_data_retrieval_data**
> delete_available_data_retrieval_data(operation_id, available_dataset_id)

Delete Retrieved Data

Deletes retrieved data living in memory. A new operation will need to be created to retrieve the data again. Requires the available_dataset_delete_data_retrieval permission.

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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    available_dataset_id = 'available_dataset_id_example' # str | 

    try:
        # Delete Retrieved Data
        api_instance.delete_available_data_retrieval_data(operation_id, available_dataset_id)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->delete_available_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **available_dataset_id** | **str**|  | 

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

# **delete_data_retrieval_data**
> delete_data_retrieval_data(operation_id, dataset_id)

Delete Retrieved Data

Deletes retrieved data living in memory. A new operation will need to be created to retrieve the data again. Requires the dataset_delete_data_retrieval permission.

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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Delete Retrieved Data
        api_instance.delete_data_retrieval_data(operation_id, dataset_id)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->delete_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **dataset_id** | **str**|  | 

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

# **get_available_data_retrieval_data**
> DataRetrievalOperation get_available_data_retrieval_data(operation_id, available_dataset_id)

Gets Raw Data Operation Data

Gets the data retrieved by raw data operation. Requires the available_dataset_get_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_retrieval_operation import DataRetrievalOperation
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    available_dataset_id = 'available_dataset_id_example' # str | 

    try:
        # Gets Raw Data Operation Data
        api_response = api_instance.get_available_data_retrieval_data(operation_id, available_dataset_id)
        print("The response of DataRetrievalV1Api->get_available_data_retrieval_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->get_available_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **available_dataset_id** | **str**|  | 

### Return type

[**DataRetrievalOperation**](DataRetrievalOperation.md)

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

# **get_data_retrieval_data**
> DataRetrievalOperation get_data_retrieval_data(operation_id, dataset_id)

Gets Raw Data Operation Data

Gets the data retrieved by raw data operation. Requires the dataset_get_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_retrieval_operation import DataRetrievalOperation
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Gets Raw Data Operation Data
        api_response = api_instance.get_data_retrieval_data(operation_id, dataset_id)
        print("The response of DataRetrievalV1Api->get_data_retrieval_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->get_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **dataset_id** | **str**|  | 

### Return type

[**DataRetrievalOperation**](DataRetrievalOperation.md)

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

# **post_available_data_retrieval_operation**
> DataRetrievalOperation post_available_data_retrieval_operation(available_dataset_id, post_data_retrieval_operation)

Create Raw Data Operation

Creates a new raw data operation. Requires the available_dataset_create_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_retrieval_operation import DataRetrievalOperation
from arthur_client.api_bindings.models.post_data_retrieval_operation import PostDataRetrievalOperation
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    available_dataset_id = 'available_dataset_id_example' # str | 
    post_data_retrieval_operation = arthur_client.api_bindings.PostDataRetrievalOperation() # PostDataRetrievalOperation | 

    try:
        # Create Raw Data Operation
        api_response = api_instance.post_available_data_retrieval_operation(available_dataset_id, post_data_retrieval_operation)
        print("The response of DataRetrievalV1Api->post_available_data_retrieval_operation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->post_available_data_retrieval_operation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **available_dataset_id** | **str**|  | 
 **post_data_retrieval_operation** | [**PostDataRetrievalOperation**](PostDataRetrievalOperation.md)|  | 

### Return type

[**DataRetrievalOperation**](DataRetrievalOperation.md)

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

# **post_data_retrieval_operation**
> DataRetrievalOperation post_data_retrieval_operation(dataset_id, post_data_retrieval_operation)

Create Raw Data Operation

Creates a new raw data operation. Requires the dataset_create_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.data_retrieval_operation import DataRetrievalOperation
from arthur_client.api_bindings.models.post_data_retrieval_operation import PostDataRetrievalOperation
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 
    post_data_retrieval_operation = arthur_client.api_bindings.PostDataRetrievalOperation() # PostDataRetrievalOperation | 

    try:
        # Create Raw Data Operation
        api_response = api_instance.post_data_retrieval_operation(dataset_id, post_data_retrieval_operation)
        print("The response of DataRetrievalV1Api->post_data_retrieval_operation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->post_data_retrieval_operation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **post_data_retrieval_operation** | [**PostDataRetrievalOperation**](PostDataRetrievalOperation.md)|  | 

### Return type

[**DataRetrievalOperation**](DataRetrievalOperation.md)

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

# **put_available_data_retrieval_data**
> object put_available_data_retrieval_data(available_dataset_id, operation_id, put_retrieved_data)

Put Retrieved Data

Place raw data for returning. Requires the available_dataset_put_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_retrieved_data import PutRetrievedData
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    available_dataset_id = 'available_dataset_id_example' # str | 
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    put_retrieved_data = arthur_client.api_bindings.PutRetrievedData() # PutRetrievedData | 

    try:
        # Put Retrieved Data
        api_response = api_instance.put_available_data_retrieval_data(available_dataset_id, operation_id, put_retrieved_data)
        print("The response of DataRetrievalV1Api->put_available_data_retrieval_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->put_available_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **available_dataset_id** | **str**|  | 
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **put_retrieved_data** | [**PutRetrievedData**](PutRetrievedData.md)|  | 

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
**202** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_data_retrieval_data**
> object put_data_retrieval_data(dataset_id, operation_id, put_retrieved_data)

Put Retrieved Data

Place raw data for returning. Requires the dataset_put_data_retrieval permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_retrieved_data import PutRetrievedData
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
    api_instance = arthur_client.api_bindings.DataRetrievalV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 
    operation_id = 'operation_id_example' # str | Operation ID of the raw data operation.
    put_retrieved_data = arthur_client.api_bindings.PutRetrievedData() # PutRetrievedData | 

    try:
        # Put Retrieved Data
        api_response = api_instance.put_data_retrieval_data(dataset_id, operation_id, put_retrieved_data)
        print("The response of DataRetrievalV1Api->put_data_retrieval_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataRetrievalV1Api->put_data_retrieval_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **operation_id** | **str**| Operation ID of the raw data operation. | 
 **put_retrieved_data** | [**PutRetrievedData**](PutRetrievedData.md)|  | 

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
**202** | Successful Response |  -  |
**500** | Internal Server Error |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

