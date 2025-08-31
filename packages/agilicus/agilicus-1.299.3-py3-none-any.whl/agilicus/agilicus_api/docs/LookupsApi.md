# agilicus_api.LookupsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_query_org_guids**](LookupsApi.md#bulk_query_org_guids) | **POST** /v1/lookups/bulk_query | List
[**lookup_org_guid**](LookupsApi.md#lookup_org_guid) | **GET** /v1/lookups/{org_id}/{guid} | Get a guid object lookup in an org


# **bulk_query_org_guids**
> ListGuidMetadataResponse bulk_query_org_guids(lookup_request)

List

Gets metadata about requested guids

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import lookups_api
from agilicus_api.model.lookup_request import LookupRequest
from agilicus_api.model.list_guid_metadata_response import ListGuidMetadataResponse
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
    api_instance = lookups_api.LookupsApi(api_client)
    lookup_request = LookupRequest(
        org_id="123",
        guids=[
            "123",
        ],
    ) # LookupRequest | 

    # example passing only required values which don't have defaults set
    try:
        # List
        api_response = api_instance.bulk_query_org_guids(lookup_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LookupsApi->bulk_query_org_guids: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_request** | [**LookupRequest**](LookupRequest.md)|  |

### Return type

[**ListGuidMetadataResponse**](ListGuidMetadataResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ListGuidMetadataResponse Mappping |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **lookup_org_guid**
> GuidMetadata lookup_org_guid(org_id, guid)

Get a guid object lookup in an org

Gets a guid

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import lookups_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.guid_metadata import GuidMetadata
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
    api_instance = lookups_api.LookupsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    guid = "1234" # str | general object uid

    # example passing only required values which don't have defaults set
    try:
        # Get a guid object lookup in an org
        api_response = api_instance.lookup_org_guid(org_id, guid)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LookupsApi->lookup_org_guid: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **guid** | **str**| general object uid |

### Return type

[**GuidMetadata**](GuidMetadata.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | GuidMetadata Mappping |  -  |
**404** | guid does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

