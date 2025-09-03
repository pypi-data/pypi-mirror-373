# arthur_client.api_bindings.JobsV1Api

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_job**](JobsV1Api.md#get_job) | **GET** /api/v1/jobs/{job_id} | Get Job By Id
[**get_job_errors**](JobsV1Api.md#get_job_errors) | **GET** /api/v1/jobs/{job_id}/runs/{job_run_id}/errors | Get Job Errors
[**get_job_logs**](JobsV1Api.md#get_job_logs) | **GET** /api/v1/jobs/{job_id}/runs/{job_run_id}/logs | Get Job Logs
[**get_job_runs**](JobsV1Api.md#get_job_runs) | **GET** /api/v1/jobs/{job_id}/runs | Get Job Runs
[**get_jobs**](JobsV1Api.md#get_jobs) | **GET** /api/v1/projects/{project_id}/jobs | List Jobs
[**post_dequeue_job**](JobsV1Api.md#post_dequeue_job) | **POST** /api/v1/data_planes/{data_plane_id}/jobs/next | Dequeue Job
[**post_job_errors**](JobsV1Api.md#post_job_errors) | **POST** /api/v1/jobs/{job_id}/runs/{job_run_id}/errors | Append To Job Errors
[**post_job_logs**](JobsV1Api.md#post_job_logs) | **POST** /api/v1/jobs/{job_id}/runs/{job_run_id}/logs | Append To Job Logs
[**post_submit_jobs_batch**](JobsV1Api.md#post_submit_jobs_batch) | **POST** /api/v1/projects/{project_id}/jobs | Submit Jobs Batch
[**put_job_state**](JobsV1Api.md#put_job_state) | **PUT** /api/v1/jobs/{job_id}/state | Update Job State
[**update_job**](JobsV1Api.md#update_job) | **PATCH** /api/v1/jobs/{job_id} | Update Job By Id


# **get_job**
> Job get_job(job_id)

Get Job By Id

Returns a single job by ID. Requires project_job_read permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job import Job
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Get Job By Id
        api_response = api_instance.get_job(job_id)
        print("The response of JobsV1Api->get_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->get_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**Job**](Job.md)

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

# **get_job_errors**
> ResourceListJobError get_job_errors(job_id, job_run_id)

Get Job Errors

Get job errors. Requires project_job_read_errors permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_job_error import ResourceListJobError
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    job_run_id = 'job_run_id_example' # str | The job run associated with the errors. Should be formatted as a UUID.

    try:
        # Get Job Errors
        api_response = api_instance.get_job_errors(job_id, job_run_id)
        print("The response of JobsV1Api->get_job_errors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->get_job_errors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **job_run_id** | **str**| The job run associated with the errors. Should be formatted as a UUID. | 

### Return type

[**ResourceListJobError**](ResourceListJobError.md)

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

# **get_job_logs**
> ResourceListJobLog get_job_logs(job_id, job_run_id, order=order)

Get Job Logs

Get job logs for a run. Requires project_job_read_logs permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_job_log import ResourceListJobLog
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    job_run_id = 'job_run_id_example' # str | The job run associated with the logs. Should be formatted as a UUID.
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)

    try:
        # Get Job Logs
        api_response = api_instance.get_job_logs(job_id, job_run_id, order=order)
        print("The response of JobsV1Api->get_job_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->get_job_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **job_run_id** | **str**| The job run associated with the logs. Should be formatted as a UUID. | 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 

### Return type

[**ResourceListJobLog**](ResourceListJobLog.md)

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

# **get_job_runs**
> ResourceListJobRun get_job_runs(job_id)

Get Job Runs

Get Job runs. Required project_job_read_runs permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.resource_list_job_run import ResourceListJobRun
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Get Job Runs
        api_response = api_instance.get_job_runs(job_id)
        print("The response of JobsV1Api->get_job_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->get_job_runs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**ResourceListJobRun**](ResourceListJobRun.md)

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

# **get_jobs**
> InfiniteResourceListJob get_jobs(project_id, sort=sort, order=order, duration_sec_greater_than=duration_sec_greater_than, duration_sec_less_than=duration_sec_less_than, started_before=started_before, started_after=started_after, queued_before=queued_before, queued_after=queued_after, ready_before=ready_before, ready_before_current_time=ready_before_current_time, ready_after=ready_after, ready_after_current_time=ready_after_current_time, finished_before=finished_before, finished_after=finished_after, kinds=kinds, exclude_kinds=exclude_kinds, states=states, error_count_above=error_count_above, data_plane_id=data_plane_id, schedule_id=schedule_id, trigger_type=trigger_type, triggered_by_user_id=triggered_by_user_id, triggered_by_user_email=triggered_by_user_email, model_id=model_id, nonce=nonce, page=page, page_size=page_size)

List Jobs

Returns jobs in the project matching the filter and sorting criteria. If multiple filters are specified, results will only be returned that match all of the specified criteria. Requires project_list_jobs permission. Note: exclude_kinds takes precedence over kinds and will exclude jobs even if they are in kinds.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.infinite_resource_list_job import InfiniteResourceListJob
from arthur_client.api_bindings.models.job_kind import JobKind
from arthur_client.api_bindings.models.job_state import JobState
from arthur_client.api_bindings.models.job_trigger import JobTrigger
from arthur_client.api_bindings.models.jobs_sort import JobsSort
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    sort = arthur_client.api_bindings.JobsSort() # JobsSort | Override the field used for sorting the returned list. Optional. (optional)
    order = arthur_client.api_bindings.SortOrder() # SortOrder | Override the sort order used. Optional. (optional)
    duration_sec_greater_than = 56 # int | Filter the results for jobs that ran for greater than or equal to this number of seconds. Optional. (optional)
    duration_sec_less_than = 56 # int | Filter the results for the jobs that ran for less than or equal to this number of seconds. Optional. (optional)
    started_before = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that started before this timestamp. Optional. (optional)
    started_after = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that started after this timestamp. Optional. (optional)
    queued_before = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that were queued before this timestamp. Optional. (optional)
    queued_after = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that were queued after this timestamp. Optional. (optional)
    ready_before = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that are ready before this timestamp. Optional. (optional)
    ready_before_current_time = False # bool | When true, filters jobs ready before the current server time. Takes precedence over ready_before. Optional. (optional) (default to False)
    ready_after = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that are ready after this timestamp. Optional. (optional)
    ready_after_current_time = False # bool | When true, filters jobs ready after the current server time. Takes precedence over ready_after. Optional. (optional) (default to False)
    finished_before = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that finished before this timestamp. Optional. (optional)
    finished_after = '2013-10-20T19:20:30+01:00' # datetime | Filter the results for the jobs that finished after this timestamp. Optional. (optional)
    kinds = [arthur_client.api_bindings.JobKind()] # List[JobKind] | Filter the results for the jobs of this kind. Optional. (optional)
    exclude_kinds = [arthur_client.api_bindings.JobKind()] # List[JobKind] | Exclude jobs of these kinds. Takes precedence over kinds. (optional)
    states = [arthur_client.api_bindings.JobState()] # List[JobState] | Filter the results for jobs in these states. Optional. (optional)
    error_count_above = 56 # int | Filter the results for the jobs that had greater than or equal to this many errors. Optional. (optional)
    data_plane_id = 'data_plane_id_example' # str | Filter the results for the jobs that were ran on this dataplane. Optional. (optional)
    schedule_id = 'schedule_id_example' # str | Filter the results for jobs associated with this schedule ID. Optional. (optional)
    trigger_type = arthur_client.api_bindings.JobTrigger() # JobTrigger | Filter the results for the jobs that were started by this trigger type. Optional. (optional)
    triggered_by_user_id = 'triggered_by_user_id_example' # str | Filter the results for the jobs that started by this user id. Only valid when trigger_type = 'user'. Optional. (optional)
    triggered_by_user_email = 'triggered_by_user_email_example' # str | Filter the results for the jobs that started by this user email. Only valid when trigger_type = 'user'. Optional. (optional)
    model_id = 'model_id_example' # str | Filter the results for jobs associated with this model ID. Includes jobs associated with datasets used by the model. Optional. (optional)
    nonce = 'nonce_example' # str | Filter the results for jobs that match a job nonce used to ensure exactly once execution. (optional)
    page = 1 # int | The page to return starting from 1 up to total_pages. (optional) (default to 1)
    page_size = 20 # int | The number of records per page. The max is 1000. (optional) (default to 20)

    try:
        # List Jobs
        api_response = api_instance.get_jobs(project_id, sort=sort, order=order, duration_sec_greater_than=duration_sec_greater_than, duration_sec_less_than=duration_sec_less_than, started_before=started_before, started_after=started_after, queued_before=queued_before, queued_after=queued_after, ready_before=ready_before, ready_before_current_time=ready_before_current_time, ready_after=ready_after, ready_after_current_time=ready_after_current_time, finished_before=finished_before, finished_after=finished_after, kinds=kinds, exclude_kinds=exclude_kinds, states=states, error_count_above=error_count_above, data_plane_id=data_plane_id, schedule_id=schedule_id, trigger_type=trigger_type, triggered_by_user_id=triggered_by_user_id, triggered_by_user_email=triggered_by_user_email, model_id=model_id, nonce=nonce, page=page, page_size=page_size)
        print("The response of JobsV1Api->get_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->get_jobs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **sort** | [**JobsSort**](.md)| Override the field used for sorting the returned list. Optional. | [optional] 
 **order** | [**SortOrder**](.md)| Override the sort order used. Optional. | [optional] 
 **duration_sec_greater_than** | **int**| Filter the results for jobs that ran for greater than or equal to this number of seconds. Optional. | [optional] 
 **duration_sec_less_than** | **int**| Filter the results for the jobs that ran for less than or equal to this number of seconds. Optional. | [optional] 
 **started_before** | **datetime**| Filter the results for the jobs that started before this timestamp. Optional. | [optional] 
 **started_after** | **datetime**| Filter the results for the jobs that started after this timestamp. Optional. | [optional] 
 **queued_before** | **datetime**| Filter the results for the jobs that were queued before this timestamp. Optional. | [optional] 
 **queued_after** | **datetime**| Filter the results for the jobs that were queued after this timestamp. Optional. | [optional] 
 **ready_before** | **datetime**| Filter the results for the jobs that are ready before this timestamp. Optional. | [optional] 
 **ready_before_current_time** | **bool**| When true, filters jobs ready before the current server time. Takes precedence over ready_before. Optional. | [optional] [default to False]
 **ready_after** | **datetime**| Filter the results for the jobs that are ready after this timestamp. Optional. | [optional] 
 **ready_after_current_time** | **bool**| When true, filters jobs ready after the current server time. Takes precedence over ready_after. Optional. | [optional] [default to False]
 **finished_before** | **datetime**| Filter the results for the jobs that finished before this timestamp. Optional. | [optional] 
 **finished_after** | **datetime**| Filter the results for the jobs that finished after this timestamp. Optional. | [optional] 
 **kinds** | [**List[JobKind]**](JobKind.md)| Filter the results for the jobs of this kind. Optional. | [optional] 
 **exclude_kinds** | [**List[JobKind]**](JobKind.md)| Exclude jobs of these kinds. Takes precedence over kinds. | [optional] 
 **states** | [**List[JobState]**](JobState.md)| Filter the results for jobs in these states. Optional. | [optional] 
 **error_count_above** | **int**| Filter the results for the jobs that had greater than or equal to this many errors. Optional. | [optional] 
 **data_plane_id** | **str**| Filter the results for the jobs that were ran on this dataplane. Optional. | [optional] 
 **schedule_id** | **str**| Filter the results for jobs associated with this schedule ID. Optional. | [optional] 
 **trigger_type** | [**JobTrigger**](.md)| Filter the results for the jobs that were started by this trigger type. Optional. | [optional] 
 **triggered_by_user_id** | **str**| Filter the results for the jobs that started by this user id. Only valid when trigger_type &#x3D; &#39;user&#39;. Optional. | [optional] 
 **triggered_by_user_email** | **str**| Filter the results for the jobs that started by this user email. Only valid when trigger_type &#x3D; &#39;user&#39;. Optional. | [optional] 
 **model_id** | **str**| Filter the results for jobs associated with this model ID. Includes jobs associated with datasets used by the model. Optional. | [optional] 
 **nonce** | **str**| Filter the results for jobs that match a job nonce used to ensure exactly once execution. | [optional] 
 **page** | **int**| The page to return starting from 1 up to total_pages. | [optional] [default to 1]
 **page_size** | **int**| The number of records per page. The max is 1000. | [optional] [default to 20]

### Return type

[**InfiniteResourceListJob**](InfiniteResourceListJob.md)

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

# **post_dequeue_job**
> JobRun post_dequeue_job(data_plane_id, job_dequeue_parameters)

Dequeue Job

Returns the next available job for processing from the data plane's job queue. Requires data_plane_jobs_dequeue_next permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job_dequeue_parameters import JobDequeueParameters
from arthur_client.api_bindings.models.job_run import JobRun
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    data_plane_id = 'data_plane_id_example' # str | 
    job_dequeue_parameters = arthur_client.api_bindings.JobDequeueParameters() # JobDequeueParameters | 

    try:
        # Dequeue Job
        api_response = api_instance.post_dequeue_job(data_plane_id, job_dequeue_parameters)
        print("The response of JobsV1Api->post_dequeue_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->post_dequeue_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_plane_id** | **str**|  | 
 **job_dequeue_parameters** | [**JobDequeueParameters**](JobDequeueParameters.md)|  | 

### Return type

[**JobRun**](JobRun.md)

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
**204** | No Content |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_job_errors**
> post_job_errors(job_id, job_run_id, job_errors)

Append To Job Errors

Append job errors. Requires project_job_append_errors permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job_errors import JobErrors
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    job_run_id = 'job_run_id_example' # str | The job run associated with the errors. Should be formatted as a UUID.
    job_errors = arthur_client.api_bindings.JobErrors() # JobErrors | 

    try:
        # Append To Job Errors
        api_instance.post_job_errors(job_id, job_run_id, job_errors)
    except Exception as e:
        print("Exception when calling JobsV1Api->post_job_errors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **job_run_id** | **str**| The job run associated with the errors. Should be formatted as a UUID. | 
 **job_errors** | [**JobErrors**](JobErrors.md)|  | 

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

# **post_job_logs**
> post_job_logs(job_id, job_run_id, job_logs)

Append To Job Logs

Append job logs. Requires project_job_append_logs permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job_logs import JobLogs
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    job_run_id = 'job_run_id_example' # str | The job run associated with the logs. Should be formatted as a UUID.
    job_logs = arthur_client.api_bindings.JobLogs() # JobLogs | 

    try:
        # Append To Job Logs
        api_instance.post_job_logs(job_id, job_run_id, job_logs)
    except Exception as e:
        print("Exception when calling JobsV1Api->post_job_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **job_run_id** | **str**| The job run associated with the logs. Should be formatted as a UUID. | 
 **job_logs** | [**JobLogs**](JobLogs.md)|  | 

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

# **post_submit_jobs_batch**
> JobsBatch post_submit_jobs_batch(project_id, post_job_batch)

Submit Jobs Batch

Submit new jobs to run. Requires project_create_job permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.jobs_batch import JobsBatch
from arthur_client.api_bindings.models.post_job_batch import PostJobBatch
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    project_id = 'project_id_example' # str | 
    post_job_batch = arthur_client.api_bindings.PostJobBatch() # PostJobBatch | 

    try:
        # Submit Jobs Batch
        api_response = api_instance.post_submit_jobs_batch(project_id, post_job_batch)
        print("The response of JobsV1Api->post_submit_jobs_batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->post_submit_jobs_batch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 
 **post_job_batch** | [**PostJobBatch**](PostJobBatch.md)|  | 

### Return type

[**JobsBatch**](JobsBatch.md)

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

# **put_job_state**
> Job put_job_state(job_id, job_run_id, put_job_state)

Update Job State

Update job state. Requires project_job_put_state permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job import Job
from arthur_client.api_bindings.models.put_job_state import PutJobState
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    job_run_id = 'job_run_id_example' # str | Job run ID associated with the state update.
    put_job_state = arthur_client.api_bindings.PutJobState() # PutJobState | 

    try:
        # Update Job State
        api_response = api_instance.put_job_state(job_id, job_run_id, put_job_state)
        print("The response of JobsV1Api->put_job_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->put_job_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **job_run_id** | **str**| Job run ID associated with the state update. | 
 **put_job_state** | [**PutJobState**](PutJobState.md)|  | 

### Return type

[**Job**](Job.md)

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

# **update_job**
> Job update_job(job_id, patch_job)

Update Job By Id

Updates a single job by ID. Requires project_job_update permission.

### Example

* OAuth Authentication (OAuth2AuthorizationCode):

```python
import arthur_client.api_bindings
from arthur_client.api_bindings.models.job import Job
from arthur_client.api_bindings.models.patch_job import PatchJob
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
    api_instance = arthur_client.api_bindings.JobsV1Api(api_client)
    job_id = 'job_id_example' # str | 
    patch_job = arthur_client.api_bindings.PatchJob() # PatchJob | 

    try:
        # Update Job By Id
        api_response = api_instance.update_job(job_id, patch_job)
        print("The response of JobsV1Api->update_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsV1Api->update_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **patch_job** | [**PatchJob**](PatchJob.md)|  | 

### Return type

[**Job**](Job.md)

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

