# agilicus_api.MetricsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_active_users**](MetricsApi.md#list_active_users) | **GET** /v1/metrics/{org_id}/active_users | View number of active users
[**list_top_users**](MetricsApi.md#list_top_users) | **GET** /v1/metrics/{org_id}/top_users | View top users


# **list_active_users**
> ListActiveUsersResponse list_active_users(org_id)

View number of active users

View number of active users

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import metrics_api
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.list_active_users_response import ListActiveUsersResponse
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
    api_instance = metrics_api.MetricsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    dt_from = "" # str | Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    dt_to = "" # str | Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    app_id = "G" # str | Application unique identifier (optional)
    sub_org_id = "1234" # str | Sub Organisation Unique identifier (optional)
    app_name = "z" # str | Application Name (optional)
    organisation = "agilicus" # str | Organisation Name (optional)
    interval = 60 # int | The size of the time intervals in seconds (optional) if omitted the server will use the default value of 60
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    resource_name = "my-application" # str | The name of the resource to query for (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)

    # example passing only required values which don't have defaults set
    try:
        # View number of active users
        api_response = api_instance.list_active_users(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MetricsApi->list_active_users: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # View number of active users
        api_response = api_instance.list_active_users(org_id, dt_from=dt_from, dt_to=dt_to, app_id=app_id, sub_org_id=sub_org_id, app_name=app_name, organisation=organisation, interval=interval, resource_type=resource_type, resource_name=resource_name, resource_id=resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MetricsApi->list_active_users: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **dt_from** | **str**| Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **dt_to** | **str**| Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **app_id** | **str**| Application unique identifier | [optional]
 **sub_org_id** | **str**| Sub Organisation Unique identifier | [optional]
 **app_name** | **str**| Application Name | [optional]
 **organisation** | **str**| Organisation Name | [optional]
 **interval** | **int**| The size of the time intervals in seconds | [optional] if omitted the server will use the default value of 60
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **resource_name** | **str**| The name of the resource to query for | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]

### Return type

[**ListActiveUsersResponse**](ListActiveUsersResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The query ran without error |  -  |
**400** | Query is invalid |  -  |
**403** | User does not have permissions to query |  -  |
**500** | Invalid database dialect |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_top_users**
> ListTopUsersResponse list_top_users(org_id)

View top users

View top users

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import metrics_api
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.list_top_users_response import ListTopUsersResponse
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
    api_instance = metrics_api.MetricsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    dt_from = "" # str | Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    dt_to = "" # str | Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    app_id = "G" # str | Application unique identifier (optional)
    sub_org_id = "1234" # str | Sub Organisation Unique identifier (optional)
    app_name = "z" # str | Application Name (optional)
    organisation = "agilicus" # str | Organisation Name (optional)
    interval = 60 # int | The size of the time intervals in seconds (optional) if omitted the server will use the default value of 60
    limit = 1 # int | limit the number of top users in the response (optional) if omitted the server will use the default value of 15
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    resource_name = "my-application" # str | The name of the resource to query for (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)

    # example passing only required values which don't have defaults set
    try:
        # View top users
        api_response = api_instance.list_top_users(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MetricsApi->list_top_users: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # View top users
        api_response = api_instance.list_top_users(org_id, dt_from=dt_from, dt_to=dt_to, app_id=app_id, sub_org_id=sub_org_id, app_name=app_name, organisation=organisation, interval=interval, limit=limit, resource_type=resource_type, resource_name=resource_name, resource_id=resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MetricsApi->list_top_users: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **dt_from** | **str**| Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **dt_to** | **str**| Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **app_id** | **str**| Application unique identifier | [optional]
 **sub_org_id** | **str**| Sub Organisation Unique identifier | [optional]
 **app_name** | **str**| Application Name | [optional]
 **organisation** | **str**| Organisation Name | [optional]
 **interval** | **int**| The size of the time intervals in seconds | [optional] if omitted the server will use the default value of 60
 **limit** | **int**| limit the number of top users in the response | [optional] if omitted the server will use the default value of 15
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **resource_name** | **str**| The name of the resource to query for | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]

### Return type

[**ListTopUsersResponse**](ListTopUsersResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The query ran without error |  -  |
**400** | Query is invalid |  -  |
**403** | User does not have permissions to query |  -  |
**500** | Invalid database dialect |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

