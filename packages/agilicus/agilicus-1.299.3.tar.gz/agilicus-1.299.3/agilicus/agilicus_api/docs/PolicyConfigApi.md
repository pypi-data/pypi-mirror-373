# agilicus_api.PolicyConfigApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_authz_bundle**](PolicyConfigApi.md#delete_authz_bundle) | **DELETE** /v1/policy_config/authz_bundle/{org_id} | Delete policy config authz bundle
[**delete_resource_url_bundle**](PolicyConfigApi.md#delete_resource_url_bundle) | **DELETE** /v1/policy_config/resource_url_bundle | Delete policy config resource url bundle
[**get_authz_bundle**](PolicyConfigApi.md#get_authz_bundle) | **GET** /v1/policy_config/authz_bundle/{org_id} | Get PolicyConfigAuthzBundle for an org
[**get_resource_url_bundle**](PolicyConfigApi.md#get_resource_url_bundle) | **GET** /v1/policy_config/resource_url_bundle | Get the global resource url bundle


# **delete_authz_bundle**
> delete_authz_bundle(org_id)

Delete policy config authz bundle

Delete policy config authz bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_config_api
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
    api_instance = policy_config_api.PolicyConfigApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier

    # example passing only required values which don't have defaults set
    try:
        # Delete policy config authz bundle
        api_instance.delete_authz_bundle(org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyConfigApi->delete_authz_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | PolicyConfigAuthzBundle deleted |  -  |
**404** | PolicyConfigAuthzBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource_url_bundle**
> delete_resource_url_bundle()

Delete policy config resource url bundle

Delete policy config resource url bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_config_api
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
    api_instance = policy_config_api.PolicyConfigApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Delete policy config resource url bundle
        api_instance.delete_resource_url_bundle()
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyConfigApi->delete_resource_url_bundle: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | PolicyConfigResourceURLBundle deleted |  -  |
**404** | PolicyConfigResourceURLBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_authz_bundle**
> PolicyConfigAuthzBundle get_authz_bundle(org_id)

Get PolicyConfigAuthzBundle for an org

Get PolicyConfigAuthzBundle for an org

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_config_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy_config_authz_bundle import PolicyConfigAuthzBundle
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
    api_instance = policy_config_api.PolicyConfigApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    if_none_match = "asdflkjasf" # str | The entity tag (etag) for a requested policy config. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get PolicyConfigAuthzBundle for an org
        api_response = api_instance.get_authz_bundle(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyConfigApi->get_authz_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get PolicyConfigAuthzBundle for an org
        api_response = api_instance.get_authz_bundle(org_id, if_none_match=if_none_match)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyConfigApi->get_authz_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **if_none_match** | **str**| The entity tag (etag) for a requested policy config. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  | [optional]

### Return type

[**PolicyConfigAuthzBundle**](PolicyConfigAuthzBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a PolicyConfigAuthzBundle |  * Etag -  <br>  |
**304** | Response not modified |  -  |
**404** | PolicyConfigAuthzBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_url_bundle**
> PolicyConfigResourceURLBundle get_resource_url_bundle()

Get the global resource url bundle

Get the global resource url bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_config_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy_config_resource_url_bundle import PolicyConfigResourceURLBundle
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
    api_instance = policy_config_api.PolicyConfigApi(api_client)
    if_none_match = "asdflkjasf" # str | The entity tag (etag) for a requested policy config. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get the global resource url bundle
        api_response = api_instance.get_resource_url_bundle(if_none_match=if_none_match)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyConfigApi->get_resource_url_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **if_none_match** | **str**| The entity tag (etag) for a requested policy config. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  | [optional]

### Return type

[**PolicyConfigResourceURLBundle**](PolicyConfigResourceURLBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a PolicyConfigResourceURLBundle |  * Etag -  <br>  |
**304** | Response not modified |  -  |
**404** | PolicyConfigResourceURLBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

