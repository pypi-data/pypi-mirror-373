# agilicus_api.FeaturesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_feature_tag**](FeaturesApi.md#add_feature_tag) | **POST** /v1/feature_tags | Add a feature tag
[**delete_feature_tag**](FeaturesApi.md#delete_feature_tag) | **DELETE** /v1/feature_tags/{feature_tag_name} | Delete a feature tag
[**get_feature_tag**](FeaturesApi.md#get_feature_tag) | **GET** /v1/feature_tags/{feature_tag_name} | Get a feature tag
[**list_feature_tags**](FeaturesApi.md#list_feature_tags) | **GET** /v1/feature_tags | List all feature_tags
[**replace_feature_tag**](FeaturesApi.md#replace_feature_tag) | **PUT** /v1/feature_tags/{feature_tag_name} | update a feature tag


# **add_feature_tag**
> FeatureTag add_feature_tag(feature_tag)

Add a feature tag

Adds a new feature tag. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import features_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.feature_tag import FeatureTag
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
    api_instance = features_api.FeaturesApi(api_client)
    feature_tag = FeatureTag(
        metadata=CommonMetadata(
        ),
        spec=FeatureTagSpec(
            name=FeatureTagName("north-america"),
        ),
    ) # FeatureTag | 

    # example passing only required values which don't have defaults set
    try:
        # Add a feature tag
        api_response = api_instance.add_feature_tag(feature_tag)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->add_feature_tag: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_tag** | [**FeatureTag**](FeatureTag.md)|  |

### Return type

[**FeatureTag**](FeatureTag.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New feature tag created |  -  |
**400** | The request is invalid |  -  |
**409** | feature tag already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_feature_tag**
> delete_feature_tag(feature_tag_name)

Delete a feature tag

Delete a feature tag

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import features_api
from agilicus_api.model.error_message import ErrorMessage
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
    api_instance = features_api.FeaturesApi(api_client)
    feature_tag_name = "ipsec-vpn" # str | A feature tag name found in the path

    # example passing only required values which don't have defaults set
    try:
        # Delete a feature tag
        api_instance.delete_feature_tag(feature_tag_name)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->delete_feature_tag: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_tag_name** | **str**| A feature tag name found in the path |

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | FeatureTag was deleted |  -  |
**404** | FeatureTag does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_feature_tag**
> FeatureTag get_feature_tag(feature_tag_name)

Get a feature tag

Get a feature tag

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import features_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.feature_tag import FeatureTag
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
    api_instance = features_api.FeaturesApi(api_client)
    feature_tag_name = "ipsec-vpn" # str | A feature tag name found in the path

    # example passing only required values which don't have defaults set
    try:
        # Get a feature tag
        api_response = api_instance.get_feature_tag(feature_tag_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->get_feature_tag: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_tag_name** | **str**| A feature tag name found in the path |

### Return type

[**FeatureTag**](FeatureTag.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a FeatureTag |  -  |
**404** | FeatureTag does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_feature_tags**
> ListFeatureTagsResponse list_feature_tags()

List all feature_tags

List all feature_tags matching the provided query parameters. Perform keyset pagination by setting the page_at_name parameter to the name for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import features_api
from agilicus_api.model.list_feature_tags_response import ListFeatureTagsResponse
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
    api_instance = features_api.FeaturesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    page_at_name = "ca-1" # str | Pagination based query with the name as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_name` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all feature_tags
        api_response = api_instance.list_feature_tags(limit=limit, name=name, page_at_name=page_at_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->list_feature_tags: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **page_at_name** | **str**| Pagination based query with the name as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_name&#x60; field from the list response.  | [optional]

### Return type

[**ListFeatureTagsResponse**](ListFeatureTagsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_feature_tag**
> FeatureTag replace_feature_tag(feature_tag_name)

update a feature tag

update a feature tag

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import features_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.feature_tag import FeatureTag
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
    api_instance = features_api.FeaturesApi(api_client)
    feature_tag_name = "ipsec-vpn" # str | A feature tag name found in the path
    feature_tag = FeatureTag(
        metadata=CommonMetadata(
        ),
        spec=FeatureTagSpec(
            name=FeatureTagName("north-america"),
        ),
    ) # FeatureTag |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a feature tag
        api_response = api_instance.replace_feature_tag(feature_tag_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->replace_feature_tag: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a feature tag
        api_response = api_instance.replace_feature_tag(feature_tag_name, feature_tag=feature_tag)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FeaturesApi->replace_feature_tag: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature_tag_name** | **str**| A feature tag name found in the path |
 **feature_tag** | [**FeatureTag**](FeatureTag.md)|  | [optional]

### Return type

[**FeatureTag**](FeatureTag.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated FeatureTag |  -  |
**400** | The request is invalid |  -  |
**404** | FeatureTag does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

