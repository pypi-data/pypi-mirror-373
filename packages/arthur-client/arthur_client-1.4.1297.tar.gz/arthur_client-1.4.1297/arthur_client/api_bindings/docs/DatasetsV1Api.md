# arthur_client.api_bindings.DatasetsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_dataset**](DatasetsV1Api.md#delete_dataset) | **DELETE** /api/v1/datasets/{dataset_id} | Delete Dataset
[**get_available_dataset**](DatasetsV1Api.md#get_available_dataset) | **GET** /api/v1/available_datasets/{available_dataset_id} | Get Available Dataset By Id
[**get_connector_available_datasets**](DatasetsV1Api.md#get_connector_available_datasets) | **GET** /api/v1/connectors/{connector_id}/available_datasets | Get Available Datasets By Connector Id
[**get_connector_datasets**](DatasetsV1Api.md#get_connector_datasets) | **GET** /api/v1/connectors/{connector_id}/datasets | Get Datasets By Connector Id
[**get_dataset**](DatasetsV1Api.md#get_dataset) | **GET** /api/v1/datasets/{dataset_id} | Get Dataset By Id
[**get_datasets**](DatasetsV1Api.md#get_datasets) | **GET** /api/v1/projects/{project_id}/datasets | Get Datasets
[**get_datasets_in_workspace**](DatasetsV1Api.md#get_datasets_in_workspace) | **GET** /api/v1/workspaces/{workspace_id}/datasets | Get Workspace Datasets.
[**patch_dataset**](DatasetsV1Api.md#patch_dataset) | **PATCH** /api/v1/datasets/{dataset_id} | Update Dataset
[**post_available_dataset**](DatasetsV1Api.md#post_available_dataset) | **POST** /api/v1/connectors/{connector_id}/available_datasets | Create Single Available Dataset
[**post_connector_dataset**](DatasetsV1Api.md#post_connector_dataset) | **POST** /api/v1/connectors/{connector_id}/datasets | Create Connector Dataset
[**post_project_available_dataset**](DatasetsV1Api.md#post_project_available_dataset) | **POST** /api/v1/projects/{project_id}/available_datasets | Create Project Available Dataset
[**post_project_dataset**](DatasetsV1Api.md#post_project_dataset) | **POST** /api/v1/projects/{project_id}/datasets | Create Project Dataset
[**put_available_dataset_schema**](DatasetsV1Api.md#put_available_dataset_schema) | **PUT** /api/v1/available_datasets/{available_dataset_id}/schema | Update Available Dataset Schema
[**put_connector_available_datasets**](DatasetsV1Api.md#put_connector_available_datasets) | **PUT** /api/v1/connectors/{connector_id}/available_datasets | Overwrite Connector Available Datasets
[**put_dataset_schema**](DatasetsV1Api.md#put_dataset_schema) | **PUT** /api/v1/datasets/{dataset_id}/schema | Update Dataset Schema


# **delete_dataset**
> delete_dataset(dataset_id)

Delete Dataset

Delete a dataset. Requires dataset_delete permission.

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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Delete Dataset
        api_instance.delete_dataset(dataset_id)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->delete_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
**204** | No Content |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_available_dataset**
> AvailableDataset get_available_dataset(available_dataset_id)

Get Available Dataset By Id

Returns a single available dataset by ID. Requires available_dataset_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.available_dataset import AvailableDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    available_dataset_id = 'available_dataset_id_example' # str | 

    try:
        # Get Available Dataset By Id
        api_response = api_instance.get_available_dataset(available_dataset_id)
        print("The response of DatasetsV1Api->get_available_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_available_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **available_dataset_id** | **str**|  | 

### Return type

[**AvailableDataset**](AvailableDataset.md)

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

# **get_connector_available_datasets**
> ResourceListAvailableDataset get_connector_available_datasets(connector_id, sort=sort, order=order, search=search, page=page, page_size=page_size)

Get Available Datasets By Connector Id

Returns a list of available datasets for the connector. Requires connector_list_available_datasets permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.available_datasets_sort import AvailableDatasetsSort
from arthur_client.api_bindings.models.resource_list_available_dataset import ResourceListAvailableDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    sort = arthur_client.api_bindings.AvailableDatasetsSort() # AvailableDatasetsSort | The field to sort by. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | The order to sort by. (optional)
    search = 'search_example' # str | Search term to filter by. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Available Datasets By Connector Id
        api_response = api_instance.get_connector_available_datasets(connector_id, sort=sort, order=order, search=search, page=page, page_size=page_size)
        print("The response of DatasetsV1Api->get_connector_available_datasets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_connector_available_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **sort** | [**AvailableDatasetsSort**](.md)| The field to sort by. | [optional] 
 **order** | [**SortOrder**](.md)| The order to sort by. | [optional] 
 **search** | **str**| Search term to filter by. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListAvailableDataset**](ResourceListAvailableDataset.md)

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

# **get_connector_datasets**
> ResourceListDataset get_connector_datasets(connector_id)

Get Datasets By Connector Id

Returns a list of configured datasets for the connector. Requires connector_list_datasets permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_dataset import ResourceListDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 

    try:
        # Get Datasets By Connector Id
        api_response = api_instance.get_connector_datasets(connector_id)
        print("The response of DatasetsV1Api->get_connector_datasets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_connector_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 

### Return type

[**ResourceListDataset**](ResourceListDataset.md)

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

# **get_dataset**
> Dataset get_dataset(dataset_id)

Get Dataset By Id

Returns a single dataset by ID. Requires dataset_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.dataset import Dataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Get Dataset By Id
        api_response = api_instance.get_dataset(dataset_id)
        print("The response of DatasetsV1Api->get_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 

### Return type

[**Dataset**](Dataset.md)

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

# **get_datasets**
> ResourceListDataset get_datasets(project_id, sort=sort, order=order, model_ids=model_ids, search=search, connector_type=connector_type, connector_name=connector_name, dataset_name=dataset_name, joined_datasets=joined_datasets, data_plane_id=data_plane_id, page=page, page_size=page_size)

Get Datasets

Returns a list of configured datasets. Requires project_list_datasets permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_type import ConnectorType
from arthur_client.api_bindings.models.datasets_sort import DatasetsSort
from arthur_client.api_bindings.models.resource_list_dataset import ResourceListDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    sort = arthur_client.api_bindings.DatasetsSort() # DatasetsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    model_ids = ['model_ids_example'] # List[str] | Filter the results for datasets that are used by these models. Optional. (optional)
    search = 'search_example' # str | Search for datasets by connector name or dataset name. (optional)
    connector_type = arthur_client.api_bindings.ConnectorType() # ConnectorType | Filter datasets by connector type. (optional)
    connector_name = 'connector_name_example' # str | Filter datasets by connector name. (optional)
    dataset_name = 'dataset_name_example' # str | Filter datasets by dataset name. (optional)
    joined_datasets = True # bool | Filter for joined datasets. Only returns joined datasets if True. Only returns non-joined datasets if False. Not applied if None. (optional)
    data_plane_id = 'data_plane_id_example' # str | Filter datasets by the data plane (engine) that backs them. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Datasets
        api_response = api_instance.get_datasets(project_id, sort=sort, order=order, model_ids=model_ids, search=search, connector_type=connector_type, connector_name=connector_name, dataset_name=dataset_name, joined_datasets=joined_datasets, data_plane_id=data_plane_id, page=page, page_size=page_size)
        print("The response of DatasetsV1Api->get_datasets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sort** | [**DatasetsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **model_ids** | [**List[str]**](str.md)| Filter the results for datasets that are used by these models. Optional. | [optional] 
 **search** | **str**| Search for datasets by connector name or dataset name. | [optional] 
 **connector_type** | [**ConnectorType**](.md)| Filter datasets by connector type. | [optional] 
 **connector_name** | **str**| Filter datasets by connector name. | [optional] 
 **dataset_name** | **str**| Filter datasets by dataset name. | [optional] 
 **joined_datasets** | **bool**| Filter for joined datasets. Only returns joined datasets if True. Only returns non-joined datasets if False. Not applied if None. | [optional] 
 **data_plane_id** | **str**| Filter datasets by the data plane (engine) that backs them. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataset**](ResourceListDataset.md)

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

# **get_datasets_in_workspace**
> ResourceListDataset get_datasets_in_workspace(workspace_id, sort=sort, order=order, model_ids=model_ids, search=search, connector_type=connector_type, connector_name=connector_name, dataset_name=dataset_name, joined_datasets=joined_datasets, data_plane_id=data_plane_id, page=page, page_size=page_size)

Get Workspace Datasets.

Endpoint requires workspace_list_datasets permission. It will only include datasets the user has additional dataset_read permissions on in the response.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.connector_type import ConnectorType
from arthur_client.api_bindings.models.datasets_sort import DatasetsSort
from arthur_client.api_bindings.models.resource_list_dataset import ResourceListDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    workspace_id = 'workspace_id_example' # str | 
    sort = arthur_client.api_bindings.DatasetsSort() # DatasetsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    model_ids = ['model_ids_example'] # List[str] | Filter the results for datasets that are used by these models. Optional. (optional)
    search = 'search_example' # str | Search for datasets by connector name or dataset name. (optional)
    connector_type = arthur_client.api_bindings.ConnectorType() # ConnectorType | Filter datasets by connector type. (optional)
    connector_name = 'connector_name_example' # str | Filter datasets by connector name. (optional)
    dataset_name = 'dataset_name_example' # str | Filter datasets by dataset name. (optional)
    joined_datasets = True # bool | Filter for joined datasets. Only returns joined datasets if True. Only returns non-joined datasets if False. Not applied if None. (optional)
    data_plane_id = 'data_plane_id_example' # str | Filter datasets by the data plane (engine) that backs them. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # Get Workspace Datasets.
        api_response = api_instance.get_datasets_in_workspace(workspace_id, sort=sort, order=order, model_ids=model_ids, search=search, connector_type=connector_type, connector_name=connector_name, dataset_name=dataset_name, joined_datasets=joined_datasets, data_plane_id=data_plane_id, page=page, page_size=page_size)
        print("The response of DatasetsV1Api->get_datasets_in_workspace:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->get_datasets_in_workspace: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **sort** | [**DatasetsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **model_ids** | [**List[str]**](str.md)| Filter the results for datasets that are used by these models. Optional. | [optional] 
 **search** | **str**| Search for datasets by connector name or dataset name. | [optional] 
 **connector_type** | [**ConnectorType**](.md)| Filter datasets by connector type. | [optional] 
 **connector_name** | **str**| Filter datasets by connector name. | [optional] 
 **dataset_name** | **str**| Filter datasets by dataset name. | [optional] 
 **joined_datasets** | **bool**| Filter for joined datasets. Only returns joined datasets if True. Only returns non-joined datasets if False. Not applied if None. | [optional] 
 **data_plane_id** | **str**| Filter datasets by the data plane (engine) that backs them. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**ResourceListDataset**](ResourceListDataset.md)

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

# **patch_dataset**
> Dataset patch_dataset(dataset_id, patch_dataset)

Update Dataset

Update a dataset. Requires dataset_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.dataset import Dataset
from arthur_client.api_bindings.models.patch_dataset import PatchDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 
    patch_dataset = arthur_client.api_bindings.PatchDataset() # PatchDataset | 

    try:
        # Update Dataset
        api_response = api_instance.patch_dataset(dataset_id, patch_dataset)
        print("The response of DatasetsV1Api->patch_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->patch_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **patch_dataset** | [**PatchDataset**](PatchDataset.md)|  | 

### Return type

[**Dataset**](Dataset.md)

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

# **post_available_dataset**
> AvailableDataset post_available_dataset(connector_id, put_available_dataset)

Create Single Available Dataset

Create a single available dataset for this connector. Requires connector_create_available_datasetpermission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.available_dataset import AvailableDataset
from arthur_client.api_bindings.models.put_available_dataset import PutAvailableDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    put_available_dataset = arthur_client.api_bindings.PutAvailableDataset() # PutAvailableDataset | 

    try:
        # Create Single Available Dataset
        api_response = api_instance.post_available_dataset(connector_id, put_available_dataset)
        print("The response of DatasetsV1Api->post_available_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->post_available_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **put_available_dataset** | [**PutAvailableDataset**](PutAvailableDataset.md)|  | 

### Return type

[**AvailableDataset**](AvailableDataset.md)

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

# **post_connector_dataset**
> Dataset post_connector_dataset(connector_id, post_dataset)

Create Connector Dataset

Create connector dataset. Requires connector_create_dataset permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.dataset import Dataset
from arthur_client.api_bindings.models.post_dataset import PostDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    post_dataset = arthur_client.api_bindings.PostDataset() # PostDataset | 

    try:
        # Create Connector Dataset
        api_response = api_instance.post_connector_dataset(connector_id, post_dataset)
        print("The response of DatasetsV1Api->post_connector_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->post_connector_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **post_dataset** | [**PostDataset**](PostDataset.md)|  | 

### Return type

[**Dataset**](Dataset.md)

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

# **post_project_available_dataset**
> AvailableDataset post_project_available_dataset(project_id, put_available_dataset)

Create Project Available Dataset

Create project dataset. Requires project_create_available_dataset permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.available_dataset import AvailableDataset
from arthur_client.api_bindings.models.put_available_dataset import PutAvailableDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    put_available_dataset = arthur_client.api_bindings.PutAvailableDataset() # PutAvailableDataset | 

    try:
        # Create Project Available Dataset
        api_response = api_instance.post_project_available_dataset(project_id, put_available_dataset)
        print("The response of DatasetsV1Api->post_project_available_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->post_project_available_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **put_available_dataset** | [**PutAvailableDataset**](PutAvailableDataset.md)|  | 

### Return type

[**AvailableDataset**](AvailableDataset.md)

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

# **post_project_dataset**
> Dataset post_project_dataset(project_id, post_dataset)

Create Project Dataset

Create project dataset. Requires project_create_dataset permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.dataset import Dataset
from arthur_client.api_bindings.models.post_dataset import PostDataset
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_dataset = arthur_client.api_bindings.PostDataset() # PostDataset | 

    try:
        # Create Project Dataset
        api_response = api_instance.post_project_dataset(project_id, post_dataset)
        print("The response of DatasetsV1Api->post_project_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->post_project_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_dataset** | [**PostDataset**](PostDataset.md)|  | 

### Return type

[**Dataset**](Dataset.md)

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

# **put_available_dataset_schema**
> AvailableDataset put_available_dataset_schema(available_dataset_id, put_dataset_schema)

Update Available Dataset Schema

Update a single available dataset schema. Requires available_dataset_put_schema permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.available_dataset import AvailableDataset
from arthur_client.api_bindings.models.put_dataset_schema import PutDatasetSchema
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    available_dataset_id = 'available_dataset_id_example' # str | 
    put_dataset_schema = arthur_client.api_bindings.PutDatasetSchema() # PutDatasetSchema | 

    try:
        # Update Available Dataset Schema
        api_response = api_instance.put_available_dataset_schema(available_dataset_id, put_dataset_schema)
        print("The response of DatasetsV1Api->put_available_dataset_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->put_available_dataset_schema: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **available_dataset_id** | **str**|  | 
 **put_dataset_schema** | [**PutDatasetSchema**](PutDatasetSchema.md)|  | 

### Return type

[**AvailableDataset**](AvailableDataset.md)

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

# **put_connector_available_datasets**
> put_connector_available_datasets(connector_id, put_available_datasets)

Overwrite Connector Available Datasets

Overwrite all available datasets for this connector. Requires connector_put_available_datasets permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.put_available_datasets import PutAvailableDatasets
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    connector_id = 'connector_id_example' # str | 
    put_available_datasets = arthur_client.api_bindings.PutAvailableDatasets() # PutAvailableDatasets | 

    try:
        # Overwrite Connector Available Datasets
        api_instance.put_connector_available_datasets(connector_id, put_available_datasets)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->put_connector_available_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**|  | 
 **put_available_datasets** | [**PutAvailableDatasets**](PutAvailableDatasets.md)|  | 

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

# **put_dataset_schema**
> Dataset put_dataset_schema(dataset_id, put_dataset_schema)

Update Dataset Schema

Update a dataset schema. Requires dataset_put_schema permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.dataset import Dataset
from arthur_client.api_bindings.models.put_dataset_schema import PutDatasetSchema
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
    api_instance = arthur_client.api_bindings.DatasetsV1Api(api_client)
    dataset_id = 'dataset_id_example' # str | 
    put_dataset_schema = arthur_client.api_bindings.PutDatasetSchema() # PutDatasetSchema | 

    try:
        # Update Dataset Schema
        api_response = api_instance.put_dataset_schema(dataset_id, put_dataset_schema)
        print("The response of DatasetsV1Api->put_dataset_schema:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsV1Api->put_dataset_schema: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **put_dataset_schema** | [**PutDatasetSchema**](PutDatasetSchema.md)|  | 

### Return type

[**Dataset**](Dataset.md)

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

