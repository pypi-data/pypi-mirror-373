# agilicus_api.HostsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_host**](HostsApi.md#add_host) | **POST** /v1/hosts | Creates a Host
[**add_host_bundle**](HostsApi.md#add_host_bundle) | **POST** /v1/host_bundles | Creates a HostBundle
[**add_host_label**](HostsApi.md#add_host_label) | **POST** /v1/host_labels | Creates a HostLabel
[**delete_host**](HostsApi.md#delete_host) | **DELETE** /v1/hosts/{host_id} | Delete a Host
[**delete_host_bundle**](HostsApi.md#delete_host_bundle) | **DELETE** /v1/host_bundles/{bundle} | Delete a HostBundle
[**delete_host_label**](HostsApi.md#delete_host_label) | **DELETE** /v1/host_labels/{label} | Delete a HostLabel
[**get_host**](HostsApi.md#get_host) | **GET** /v1/hosts/{host_id} | Get a Host
[**get_host_bundle**](HostsApi.md#get_host_bundle) | **GET** /v1/host_bundles/{bundle} | Get a HostBundle
[**get_host_label**](HostsApi.md#get_host_label) | **GET** /v1/host_labels/{label} | Get a HostLabel
[**list_host_bundles**](HostsApi.md#list_host_bundles) | **GET** /v1/host_bundles | list HostBundle
[**list_host_labels**](HostsApi.md#list_host_labels) | **GET** /v1/host_labels | list HostLabel
[**list_host_orgs**](HostsApi.md#list_host_orgs) | **GET** /v1/hosts/orgs | list orgs that have available hosts
[**list_hosts**](HostsApi.md#list_hosts) | **GET** /v1/hosts | list hosts
[**replace_host**](HostsApi.md#replace_host) | **PUT** /v1/hosts/{host_id} | Update a Host
[**replace_host_bundle**](HostsApi.md#replace_host_bundle) | **PUT** /v1/host_bundles/{bundle} | Update a HostBundle


# **add_host**
> Host add_host(host)

Creates a Host

Creates a Host 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.host import Host
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
    api_instance = hosts_api.HostsApi(api_client)
    host = Host(
        metadata=MetadataWithId(),
        spec=HostSpec(
            hostname=Domain("uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr"),
            port=NetworkPort("5005-5010"),
            path="path_example",
            labels=[
                HostLabelName("labels_example"),
            ],
        ),
    ) # Host | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a Host
        api_response = api_instance.add_host(host)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->add_host: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host** | [**Host**](Host.md)|  |

### Return type

[**Host**](Host.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Host created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_host_bundle**
> HostBundle add_host_bundle(host_bundle)

Creates a HostBundle

Creates a HostBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.host_bundle import HostBundle
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
    api_instance = hosts_api.HostsApi(api_client)
    host_bundle = HostBundle(
        metadata=MetadataWithId(),
        spec=HostBundleSpec(
            name=HostBundleName("0"),
            org_id="123",
            labels=[
                HostBundleLabel(
                    exclude=True,
                    label=HostLabelSpec(
                        name=HostLabelName("0"),
                        org_id="123",
                    ),
                ),
            ],
            destination=[
                HostDestination(
                    host="host_example",
                ),
            ],
        ),
        status=HostBundleStatus(
            hosts=[
                Host(
                    metadata=MetadataWithId(),
                    spec=HostSpec(
                        hostname=Domain("uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr"),
                        port=NetworkPort("5005-5010"),
                        path="path_example",
                        labels=[
                            HostLabelName("labels_example"),
                        ],
                    ),
                ),
            ],
            destination=[
                HostDestination(
                    host="host_example",
                ),
            ],
        ),
    ) # HostBundle | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a HostBundle
        api_response = api_instance.add_host_bundle(host_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->add_host_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_bundle** | [**HostBundle**](HostBundle.md)|  |

### Return type

[**HostBundle**](HostBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | HostBundle created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_host_label**
> HostLabel add_host_label(host_label)

Creates a HostLabel

Creates a HostLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.host_label import HostLabel
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
    api_instance = hosts_api.HostsApi(api_client)
    host_label = HostLabel(
        metadata=CommonMetadata(
        ),
        spec=HostLabelSpec(
            name=HostLabelName("0"),
            org_id="123",
        ),
    ) # HostLabel | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a HostLabel
        api_response = api_instance.add_host_label(host_label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->add_host_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_label** | [**HostLabel**](HostLabel.md)|  |

### Return type

[**HostLabel**](HostLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | HostLabel created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_host**
> delete_host(host_id)

Delete a Host

Delete a Host

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
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
    api_instance = hosts_api.HostsApi(api_client)
    host_id = "1234" # str | A host id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a Host
        api_instance.delete_host(host_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a Host
        api_instance.delete_host(host_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_id** | **str**| A host id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

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
**204** | Host was deleted |  -  |
**404** | Host does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_host_bundle**
> delete_host_bundle(bundle)

Delete a HostBundle

Delete a HostBundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.trusted_certificate_bundle_name import TrustedCertificateBundleName
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
    api_instance = hosts_api.HostsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a HostBundle
        api_instance.delete_host_bundle(bundle)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a HostBundle
        api_instance.delete_host_bundle(bundle, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bundle** | **TrustedCertificateBundleName**| A TrustedCertificateBundleName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

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
**204** | HostBundle was deleted |  -  |
**404** | HostBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_host_label**
> delete_host_label(label)

Delete a HostLabel

Delete a HostLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.trusted_certificate_label_name import TrustedCertificateLabelName
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
    api_instance = hosts_api.HostsApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a HostLabel
        api_instance.delete_host_label(label)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a HostLabel
        api_instance.delete_host_label(label, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->delete_host_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label** | **TrustedCertificateLabelName**| A TrustedCertificateLabelName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

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
**204** | HostLabel was deleted |  -  |
**404** | HostLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_host**
> Host get_host(host_id)

Get a Host

Get a Host

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.host import Host
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
    api_instance = hosts_api.HostsApi(api_client)
    host_id = "1234" # str | A host id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a Host
        api_response = api_instance.get_host(host_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a Host
        api_response = api_instance.get_host(host_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_id** | **str**| A host id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Host**](Host.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Host found and returned |  -  |
**404** | Host does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_host_bundle**
> HostBundle get_host_bundle(bundle)

Get a HostBundle

Get a HostBundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.trusted_certificate_bundle_name import TrustedCertificateBundleName
from agilicus_api.model.host_bundle import HostBundle
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
    api_instance = hosts_api.HostsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a HostBundle
        api_response = api_instance.get_host_bundle(bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a HostBundle
        api_response = api_instance.get_host_bundle(bundle, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bundle** | **TrustedCertificateBundleName**| A TrustedCertificateBundleName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**HostBundle**](HostBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | HostBundle found and returned |  -  |
**404** | HostBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_host_label**
> HostLabel get_host_label(label)

Get a HostLabel

Get a HostLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.host_label import HostLabel
from agilicus_api.model.trusted_certificate_label_name import TrustedCertificateLabelName
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
    api_instance = hosts_api.HostsApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a HostLabel
        api_response = api_instance.get_host_label(label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a HostLabel
        api_response = api_instance.get_host_label(label, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->get_host_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label** | **TrustedCertificateLabelName**| A TrustedCertificateLabelName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**HostLabel**](HostLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | HostLabel found and returned |  -  |
**404** | HostLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_host_bundles**
> ListHostBundle list_host_bundles()

list HostBundle

List HostBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.list_host_bundle import ListHostBundle
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
    api_instance = hosts_api.HostsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list HostBundle
        api_response = api_instance.list_host_bundles(limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->list_host_bundles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListHostBundle**](ListHostBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of HostBundle |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_host_labels**
> ListHostLabel list_host_labels()

list HostLabel

List HostLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.list_host_label import ListHostLabel
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
    api_instance = hosts_api.HostsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list HostLabel
        api_response = api_instance.list_host_labels(limit=limit, org_id=org_id, label=label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->list_host_labels: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]

### Return type

[**ListHostLabel**](ListHostLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of HostLabel |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_host_orgs**
> ListHostOrg list_host_orgs()

list orgs that have available hosts

List orgs that have available hosts 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.list_host_org import ListHostOrg
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
    api_instance = hosts_api.HostsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list orgs that have available hosts
        api_response = api_instance.list_host_orgs(org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->list_host_orgs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListHostOrg**](ListHostOrg.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list HostOrg |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_hosts**
> ListHost list_hosts()

list hosts

List hosts 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.list_host import ListHost
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
    api_instance = hosts_api.HostsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    hostname = "hostname_example" # str | hostname query lookup (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list hosts
        api_response = api_instance.list_hosts(limit=limit, org_id=org_id, label=label, page_at_id=page_at_id, hostname=hostname)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->list_hosts: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **hostname** | **str**| hostname query lookup | [optional]

### Return type

[**ListHost**](ListHost.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of Hosts |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_host**
> Host replace_host(host_id, host)

Update a Host

Update a Host 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.host import Host
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
    api_instance = hosts_api.HostsApi(api_client)
    host_id = "1234" # str | A host id
    host = Host(
        metadata=MetadataWithId(),
        spec=HostSpec(
            hostname=Domain("uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr"),
            port=NetworkPort("5005-5010"),
            path="path_example",
            labels=[
                HostLabelName("labels_example"),
            ],
        ),
    ) # Host | 

    # example passing only required values which don't have defaults set
    try:
        # Update a Host
        api_response = api_instance.replace_host(host_id, host)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->replace_host: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **host_id** | **str**| A host id |
 **host** | [**Host**](Host.md)|  |

### Return type

[**Host**](Host.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Host updated. |  -  |
**400** | The contents of the request body are invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_host_bundle**
> HostBundle replace_host_bundle(bundle, host_bundle)

Update a HostBundle

Update a HostBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import hosts_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.trusted_certificate_bundle_name import TrustedCertificateBundleName
from agilicus_api.model.host_bundle import HostBundle
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
    api_instance = hosts_api.HostsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    host_bundle = HostBundle(
        metadata=MetadataWithId(),
        spec=HostBundleSpec(
            name=HostBundleName("0"),
            org_id="123",
            labels=[
                HostBundleLabel(
                    exclude=True,
                    label=HostLabelSpec(
                        name=HostLabelName("0"),
                        org_id="123",
                    ),
                ),
            ],
            destination=[
                HostDestination(
                    host="host_example",
                ),
            ],
        ),
        status=HostBundleStatus(
            hosts=[
                Host(
                    metadata=MetadataWithId(),
                    spec=HostSpec(
                        hostname=Domain("uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr"),
                        port=NetworkPort("5005-5010"),
                        path="path_example",
                        labels=[
                            HostLabelName("labels_example"),
                        ],
                    ),
                ),
            ],
            destination=[
                HostDestination(
                    host="host_example",
                ),
            ],
        ),
    ) # HostBundle | 

    # example passing only required values which don't have defaults set
    try:
        # Update a HostBundle
        api_response = api_instance.replace_host_bundle(bundle, host_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling HostsApi->replace_host_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bundle** | **TrustedCertificateBundleName**| A TrustedCertificateBundleName |
 **host_bundle** | [**HostBundle**](HostBundle.md)|  |

### Return type

[**HostBundle**](HostBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | HostBundle udpated |  -  |
**400** | The contents of the request body are invalid |  -  |
**409** | bundle name already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

