# agilicus_api.DiagnosticsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_logs**](DiagnosticsApi.md#list_logs) | **GET** /v1/diagnostics/logs | Retrieve application logs


# **list_logs**
> ListLogsResponse list_logs(org_id)

Retrieve application logs

Retrieve application diagnostic logs. These are the output from stdout/stderr (stream). 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import diagnostics_api
from agilicus_api.model.list_logs_response import ListLogsResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = diagnostics_api.DiagnosticsApi(api_client)
    org_id = "org_id_example" # str | query for a specific organization
    dt_from = "dt_from_example" # str | search criteria, search logs from (optional)
    dt_to = "dt_to_example" # str | search criteria, search logs to (optional)
    app = "app_example" # str | search criteria, search logs for an app (optional)
    sub = "123" # str | search criteria, search logs for a given subject (USER) GUID (optional)
    limit = 150 # int | limit number of output logs (optional) if omitted the server will use the default value of 150
    sub_org_id = "sub_org_id_example" # str | query for a specific sub-organization (optional)
    env = "env_example" # str | query for a specific environment (optional)
    dt_sort = "asc" # str | Sort order: *'asc' - ascending, from old to new logs *'desc' - descending, from new to old logs  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Retrieve application logs
        api_response = api_instance.list_logs(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling DiagnosticsApi->list_logs: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Retrieve application logs
        api_response = api_instance.list_logs(org_id, dt_from=dt_from, dt_to=dt_to, app=app, sub=sub, limit=limit, sub_org_id=sub_org_id, env=env, dt_sort=dt_sort)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling DiagnosticsApi->list_logs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| query for a specific organization |
 **dt_from** | **str**| search criteria, search logs from | [optional]
 **dt_to** | **str**| search criteria, search logs to | [optional]
 **app** | **str**| search criteria, search logs for an app | [optional]
 **sub** | **str**| search criteria, search logs for a given subject (USER) GUID | [optional]
 **limit** | **int**| limit number of output logs | [optional] if omitted the server will use the default value of 150
 **sub_org_id** | **str**| query for a specific sub-organization | [optional]
 **env** | **str**| query for a specific environment | [optional]
 **dt_sort** | **str**| Sort order: *&#39;asc&#39; - ascending, from old to new logs *&#39;desc&#39; - descending, from new to old logs  | [optional]

### Return type

[**ListLogsResponse**](ListLogsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return logs in JSON format for specified parameters |  -  |
**400** | Query is invalid |  -  |
**401** | Unauthorized access |  -  |
**403** | User does not have permissions to query |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

