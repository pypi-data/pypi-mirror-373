# agilicus_api.CataloguesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_catalogue**](CataloguesApi.md#create_catalogue) | **POST** /v1/catalogues | create a catalogue
[**create_catalogue_entry**](CataloguesApi.md#create_catalogue_entry) | **POST** /v1/catalogues/{catalogue_id}/catalogue_entries | create a catalogue entry
[**delete_catalogue**](CataloguesApi.md#delete_catalogue) | **DELETE** /v1/catalogues/{catalogue_id} | Delete the catalogue specified by catalogue_id
[**delete_catalogue_entry**](CataloguesApi.md#delete_catalogue_entry) | **DELETE** /v1/catalogues/{catalogue_id}/catalogue_entries/{catalogue_entry_id} | Delete the catalogue specified by catalogue_entry_id
[**get_catalogue**](CataloguesApi.md#get_catalogue) | **GET** /v1/catalogues/{catalogue_id} | Get the catalogue specified by catalogue_id
[**get_catalogue_entry**](CataloguesApi.md#get_catalogue_entry) | **GET** /v1/catalogues/{catalogue_id}/catalogue_entries/{catalogue_entry_id} | Get the catalogue entry by id for the given catalogue
[**list_all_catalogue_entries**](CataloguesApi.md#list_all_catalogue_entries) | **GET** /v1/catalogue_entries | List all catalogue entries independant of the catalogue they belong to
[**list_catalogue_entries**](CataloguesApi.md#list_catalogue_entries) | **GET** /v1/catalogues/{catalogue_id}/catalogue_entries | List catalogue entries in the catalogue
[**list_catalogues**](CataloguesApi.md#list_catalogues) | **GET** /v1/catalogues | List all catalogues
[**replace_catalogue**](CataloguesApi.md#replace_catalogue) | **PUT** /v1/catalogues/{catalogue_id} | Replace the catalogue specified by catalogue_id
[**replace_catalogue_entry**](CataloguesApi.md#replace_catalogue_entry) | **PUT** /v1/catalogues/{catalogue_id}/catalogue_entries/{catalogue_entry_id} | Replace the catalogue entry specified by catalogue_entry_id


# **create_catalogue**
> Catalogue create_catalogue(catalogue)

create a catalogue

create a catalogue

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.catalogue import Catalogue
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue = Catalogue(
        category="category_example",
    ) # Catalogue | Catalogue

    # example passing only required values which don't have defaults set
    try:
        # create a catalogue
        api_response = api_instance.create_catalogue(catalogue)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->create_catalogue: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue** | [**Catalogue**](Catalogue.md)| Catalogue |

### Return type

[**Catalogue**](Catalogue.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully created catalogue |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_catalogue_entry**
> CatalogueEntry create_catalogue_entry(catalogue_id, catalogue_entry)

create a catalogue entry

create a catalogue entry

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.catalogue_entry import CatalogueEntry
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    catalogue_entry = CatalogueEntry(
        name="dotnet_core",
        content="cr.agilicus.com/dotnet_core/app-image:latest",
        tag="V1.1",
        short_description="short_description_example",
        long_description="long_description_example",
    ) # CatalogueEntry | CatalogueEntry

    # example passing only required values which don't have defaults set
    try:
        # create a catalogue entry
        api_response = api_instance.create_catalogue_entry(catalogue_id, catalogue_entry)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->create_catalogue_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **catalogue_entry** | [**CatalogueEntry**](CatalogueEntry.md)| CatalogueEntry |

### Return type

[**CatalogueEntry**](CatalogueEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully created catalogue entry |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_catalogue**
> delete_catalogue(catalogue_id)

Delete the catalogue specified by catalogue_id

Delete the catalogue specified by catalogue_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path

    # example passing only required values which don't have defaults set
    try:
        # Delete the catalogue specified by catalogue_id
        api_instance.delete_catalogue(catalogue_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->delete_catalogue: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |

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
**204** | Catalogue was deleted |  -  |
**404** | Catalogue not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_catalogue_entry**
> delete_catalogue_entry(catalogue_id, catalogue_entry_id)

Delete the catalogue specified by catalogue_entry_id

Delete the catalogue specified by catalogue_entry_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    catalogue_entry_id = "1234" # str | catalogue_entry_id path

    # example passing only required values which don't have defaults set
    try:
        # Delete the catalogue specified by catalogue_entry_id
        api_instance.delete_catalogue_entry(catalogue_id, catalogue_entry_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->delete_catalogue_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **catalogue_entry_id** | **str**| catalogue_entry_id path |

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
**204** | Catalogue entry was deleted |  -  |
**404** | Catalogue entry not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalogue**
> Catalogue get_catalogue(catalogue_id)

Get the catalogue specified by catalogue_id

Get the catalogue specified by catalogue_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.catalogue import Catalogue
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path

    # example passing only required values which don't have defaults set
    try:
        # Get the catalogue specified by catalogue_id
        api_response = api_instance.get_catalogue(catalogue_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->get_catalogue: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |

### Return type

[**Catalogue**](Catalogue.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the catalogue by id |  -  |
**404** | Catalogue not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_catalogue_entry**
> CatalogueEntry get_catalogue_entry(catalogue_id, catalogue_entry_id)

Get the catalogue entry by id for the given catalogue

Get the catalogue entry by id for the given catalogue

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.catalogue_entry import CatalogueEntry
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    catalogue_entry_id = "1234" # str | catalogue_entry_id path

    # example passing only required values which don't have defaults set
    try:
        # Get the catalogue entry by id for the given catalogue
        api_response = api_instance.get_catalogue_entry(catalogue_id, catalogue_entry_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->get_catalogue_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **catalogue_entry_id** | **str**| catalogue_entry_id path |

### Return type

[**CatalogueEntry**](CatalogueEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the catalogue entry by id |  -  |
**404** | Catalogue Entry not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_all_catalogue_entries**
> ListCatalogueEntriesResponse list_all_catalogue_entries()

List all catalogue entries independant of the catalogue they belong to

List all catalogue entries independant of the catalogue they belong to

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.list_catalogue_entries_response import ListCatalogueEntriesResponse
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    catalogue_entry_name = "dotnet_core" # str | Query based on a catalogue entries name (optional)
    catalogue_category = "runtimes" # str | Query based on a catalogue's category (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all catalogue entries independant of the catalogue they belong to
        api_response = api_instance.list_all_catalogue_entries(limit=limit, catalogue_entry_name=catalogue_entry_name, catalogue_category=catalogue_category)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->list_all_catalogue_entries: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **catalogue_entry_name** | **str**| Query based on a catalogue entries name | [optional]
 **catalogue_category** | **str**| Query based on a catalogue&#39;s category | [optional]

### Return type

[**ListCatalogueEntriesResponse**](ListCatalogueEntriesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of all catalogue entries |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_catalogue_entries**
> ListCatalogueEntriesResponse list_catalogue_entries(catalogue_id)

List catalogue entries in the catalogue

List catalogue entries in the catalogue

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.list_catalogue_entries_response import ListCatalogueEntriesResponse
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    catalogue_entry_name = "dotnet_core" # str | Query based on a catalogue entries name (optional)

    # example passing only required values which don't have defaults set
    try:
        # List catalogue entries in the catalogue
        api_response = api_instance.list_catalogue_entries(catalogue_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->list_catalogue_entries: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List catalogue entries in the catalogue
        api_response = api_instance.list_catalogue_entries(catalogue_id, limit=limit, catalogue_entry_name=catalogue_entry_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->list_catalogue_entries: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **catalogue_entry_name** | **str**| Query based on a catalogue entries name | [optional]

### Return type

[**ListCatalogueEntriesResponse**](ListCatalogueEntriesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of catalogue entries for the given catalogue |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_catalogues**
> ListCataloguesResponse list_catalogues()

List all catalogues

List all catalogues

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.list_catalogues_response import ListCataloguesResponse
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    catalogue_category = "runtimes" # str | Query based on a catalogue's category (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all catalogues
        api_response = api_instance.list_catalogues(limit=limit, catalogue_category=catalogue_category)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->list_catalogues: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **catalogue_category** | **str**| Query based on a catalogue&#39;s category | [optional]

### Return type

[**ListCataloguesResponse**](ListCataloguesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of all catalogues |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_catalogue**
> Catalogue replace_catalogue(catalogue_id, catalogue)

Replace the catalogue specified by catalogue_id

Replace the catalogue specified by catalogue_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.catalogue import Catalogue
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    catalogue = Catalogue(
        category="category_example",
    ) # Catalogue | Catalogue

    # example passing only required values which don't have defaults set
    try:
        # Replace the catalogue specified by catalogue_id
        api_response = api_instance.replace_catalogue(catalogue_id, catalogue)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->replace_catalogue: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **catalogue** | [**Catalogue**](Catalogue.md)| Catalogue |

### Return type

[**Catalogue**](Catalogue.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the updated catalogue |  -  |
**404** | Catalogue not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_catalogue_entry**
> CatalogueEntry replace_catalogue_entry(catalogue_id, catalogue_entry_id, catalogue_entry)

Replace the catalogue entry specified by catalogue_entry_id

Replace the catalogue entry specified by catalogue_entry_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import catalogues_api
from agilicus_api.model.catalogue_entry import CatalogueEntry
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
    api_instance = catalogues_api.CataloguesApi(api_client)
    catalogue_id = "1234" # str | catalogue_id path
    catalogue_entry_id = "1234" # str | catalogue_entry_id path
    catalogue_entry = CatalogueEntry(
        name="dotnet_core",
        content="cr.agilicus.com/dotnet_core/app-image:latest",
        tag="V1.1",
        short_description="short_description_example",
        long_description="long_description_example",
    ) # CatalogueEntry | CatalogueEntry

    # example passing only required values which don't have defaults set
    try:
        # Replace the catalogue entry specified by catalogue_entry_id
        api_response = api_instance.replace_catalogue_entry(catalogue_id, catalogue_entry_id, catalogue_entry)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CataloguesApi->replace_catalogue_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **catalogue_id** | **str**| catalogue_id path |
 **catalogue_entry_id** | **str**| catalogue_entry_id path |
 **catalogue_entry** | [**CatalogueEntry**](CatalogueEntry.md)| CatalogueEntry |

### Return type

[**CatalogueEntry**](CatalogueEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the updated catalogue |  -  |
**404** | Catalogue not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

