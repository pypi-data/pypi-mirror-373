# agilicus_api.TrustedCertsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_bundle**](TrustedCertsApi.md#create_bundle) | **POST** /v1/trusted_cert_bundles | Creates a TrustedCertificateBundle
[**create_label**](TrustedCertsApi.md#create_label) | **POST** /v1/trusted_cert_labels | Creates a TrustedCertificateLabel
[**create_trusted_cert**](TrustedCertsApi.md#create_trusted_cert) | **POST** /v1/trusted_certs | Creates a TrustedCertificate
[**delete_bundle**](TrustedCertsApi.md#delete_bundle) | **DELETE** /v1/trusted_cert_bundles/{bundle} | Delete a TrustedCertificateBundle
[**delete_label**](TrustedCertsApi.md#delete_label) | **DELETE** /v1/trusted_cert_labels/{label} | Delete a TrustedCertificateLabel
[**delete_trusted_cert**](TrustedCertsApi.md#delete_trusted_cert) | **DELETE** /v1/trusted_certs/{certificate_id} | Delete a TrustedCertificate
[**get_bundle**](TrustedCertsApi.md#get_bundle) | **GET** /v1/trusted_cert_bundles/{bundle} | Get a TrustedCertificateBundle
[**get_label**](TrustedCertsApi.md#get_label) | **GET** /v1/trusted_cert_labels/{label} | Get a TrustedCertificateLabel
[**get_trusted_cert**](TrustedCertsApi.md#get_trusted_cert) | **GET** /v1/trusted_certs/{certificate_id} | Get a TrustedCertificate
[**list_bundles**](TrustedCertsApi.md#list_bundles) | **GET** /v1/trusted_cert_bundles | list TrustedCertificateBundle
[**list_cert_orgs**](TrustedCertsApi.md#list_cert_orgs) | **GET** /v1/trusted_certs/orgs | list orgs that have available certificates
[**list_labels**](TrustedCertsApi.md#list_labels) | **GET** /v1/trusted_cert_labels | list TrustedCertificateLabel
[**list_trusted_certs**](TrustedCertsApi.md#list_trusted_certs) | **GET** /v1/trusted_certs | list certificates
[**replace_bundle**](TrustedCertsApi.md#replace_bundle) | **PUT** /v1/trusted_cert_bundles/{bundle} | Update a TrustedCertificateBundle
[**replace_trusted_cert**](TrustedCertsApi.md#replace_trusted_cert) | **PUT** /v1/trusted_certs/{certificate_id} | Update a TrustedCertificate


# **create_bundle**
> TrustedCertificateBundle create_bundle(trusted_certificate_bundle)

Creates a TrustedCertificateBundle

Creates a TrustedCertificateBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate_bundle import TrustedCertificateBundle
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    trusted_certificate_bundle = TrustedCertificateBundle(
        metadata=MetadataWithId(),
        spec=TrustedCertificateBundleSpec(
            name=TrustedCertificateBundleName("0"),
            org_id="123",
            labels=[
                TrustedCertificateBundleLabel(
                    exclude=True,
                    label=TrustedCertificateLabelSpec(
                        name=TrustedCertificateLabelName("0"),
                        org_id="123",
                    ),
                ),
            ],
        ),
        status=TrustedCertificateBundleStatus(
            trusted_certs=[
                TrustedCertificate(
                    metadata=MetadataWithId(),
                    spec=TrustedCertificateSpec(
                        root=False,
                        certificate="certificate_example",
                        org_id="123",
                        labels=[
                            TrustedCertificateLabelName("labels_example"),
                        ],
                    ),
                    status=TrustedCertificateStatus(
                    ),
                ),
            ],
            trusted_certs_etag="trusted_certs_etag_example",
        ),
    ) # TrustedCertificateBundle | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a TrustedCertificateBundle
        api_response = api_instance.create_bundle(trusted_certificate_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->create_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trusted_certificate_bundle** | [**TrustedCertificateBundle**](TrustedCertificateBundle.md)|  |

### Return type

[**TrustedCertificateBundle**](TrustedCertificateBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | TrustedCertificateBundle created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_label**
> TrustedCertificateLabel create_label(trusted_certificate_label)

Creates a TrustedCertificateLabel

Creates a TrustedCertificateLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate_label import TrustedCertificateLabel
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    trusted_certificate_label = TrustedCertificateLabel(
        metadata=CommonMetadata(
        ),
        spec=TrustedCertificateLabelSpec(
            name=TrustedCertificateLabelName("0"),
            org_id="123",
        ),
        status=TrustedCertificateLabelStatus(
        ),
    ) # TrustedCertificateLabel | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a TrustedCertificateLabel
        api_response = api_instance.create_label(trusted_certificate_label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->create_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trusted_certificate_label** | [**TrustedCertificateLabel**](TrustedCertificateLabel.md)|  |

### Return type

[**TrustedCertificateLabel**](TrustedCertificateLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | TrustedCertificateLabel created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_trusted_cert**
> TrustedCertificate create_trusted_cert(trusted_certificate)

Creates a TrustedCertificate

Creates a TrustedCertificate 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate import TrustedCertificate
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    trusted_certificate = TrustedCertificate(
        metadata=MetadataWithId(),
        spec=TrustedCertificateSpec(
            root=False,
            certificate="certificate_example",
            org_id="123",
            labels=[
                TrustedCertificateLabelName("labels_example"),
            ],
        ),
        status=TrustedCertificateStatus(
        ),
    ) # TrustedCertificate | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a TrustedCertificate
        api_response = api_instance.create_trusted_cert(trusted_certificate)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->create_trusted_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trusted_certificate** | [**TrustedCertificate**](TrustedCertificate.md)|  |

### Return type

[**TrustedCertificate**](TrustedCertificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | TrustedCertificate created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_bundle**
> delete_bundle(bundle)

Delete a TrustedCertificateBundle

Delete a TrustedCertificateBundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a TrustedCertificateBundle
        api_instance.delete_bundle(bundle)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a TrustedCertificateBundle
        api_instance.delete_bundle(bundle, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_bundle: %s\n" % e)
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
**204** | TrustedCertificateBundle was deleted |  -  |
**404** | TrustedCertificateBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_label**
> delete_label(label)

Delete a TrustedCertificateLabel

Delete a TrustedCertificateLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a TrustedCertificateLabel
        api_instance.delete_label(label)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a TrustedCertificateLabel
        api_instance.delete_label(label, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_label: %s\n" % e)
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
**204** | TrustedCertificateLabel was deleted |  -  |
**404** | TrustedCertificateLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_trusted_cert**
> delete_trusted_cert(certificate_id)

Delete a TrustedCertificate

Delete a TrustedCertificate

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    certificate_id = "1234" # str | A certificate id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a TrustedCertificate
        api_instance.delete_trusted_cert(certificate_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_trusted_cert: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a TrustedCertificate
        api_instance.delete_trusted_cert(certificate_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->delete_trusted_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_id** | **str**| A certificate id |
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
**204** | TrustedCertificate was deleted |  -  |
**404** | TrustedCertificate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bundle**
> TrustedCertificateBundle get_bundle(bundle)

Get a TrustedCertificateBundle

Get a TrustedCertificateBundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate_bundle import TrustedCertificateBundle
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    org_id = "1234" # str | Organisation Unique identifier (optional)
    trusted_cert_bundle_etag = "asdflkjasf" # str | The entity tag (etag) for a requested bundle. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  (optional)
    get_certs = True # bool | When querying a bundle, return all certs associated with bundle  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a TrustedCertificateBundle
        api_response = api_instance.get_bundle(bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a TrustedCertificateBundle
        api_response = api_instance.get_bundle(bundle, org_id=org_id, trusted_cert_bundle_etag=trusted_cert_bundle_etag, get_certs=get_certs)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bundle** | **TrustedCertificateBundleName**| A TrustedCertificateBundleName |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **trusted_cert_bundle_etag** | **str**| The entity tag (etag) for a requested bundle. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  | [optional]
 **get_certs** | **bool**| When querying a bundle, return all certs associated with bundle  | [optional]

### Return type

[**TrustedCertificateBundle**](TrustedCertificateBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | TrustedCertificateBundle found and returned |  -  |
**304** | no changes based on the input trusted_cert_bundle_etag_query  |  -  |
**404** | TrustedCertificateBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_label**
> TrustedCertificateLabel get_label(label)

Get a TrustedCertificateLabel

Get a TrustedCertificateLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate_label_name import TrustedCertificateLabelName
from agilicus_api.model.trusted_certificate_label import TrustedCertificateLabel
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a TrustedCertificateLabel
        api_response = api_instance.get_label(label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a TrustedCertificateLabel
        api_response = api_instance.get_label(label, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label** | **TrustedCertificateLabelName**| A TrustedCertificateLabelName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**TrustedCertificateLabel**](TrustedCertificateLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | TrustedCertificateLabel found and returned |  -  |
**404** | TrustedCertificateLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_trusted_cert**
> TrustedCertificate get_trusted_cert(certificate_id)

Get a TrustedCertificate

Get a TrustedCertificate

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate import TrustedCertificate
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    certificate_id = "1234" # str | A certificate id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a TrustedCertificate
        api_response = api_instance.get_trusted_cert(certificate_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_trusted_cert: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a TrustedCertificate
        api_response = api_instance.get_trusted_cert(certificate_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->get_trusted_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_id** | **str**| A certificate id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**TrustedCertificate**](TrustedCertificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | TrustedCertificate found and returned |  -  |
**404** | TrustedCertificate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_bundles**
> ListTrustedCertificateBundle list_bundles()

list TrustedCertificateBundle

List TrustedCertificateBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.list_trusted_certificate_bundle import ListTrustedCertificateBundle
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list TrustedCertificateBundle
        api_response = api_instance.list_bundles(limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->list_bundles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListTrustedCertificateBundle**](ListTrustedCertificateBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of TrustedCertificateBundle |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_cert_orgs**
> ListTrustedCertificateOrg list_cert_orgs()

list orgs that have available certificates

List orgs that have available trusted certificates 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.list_trusted_certificate_org import ListTrustedCertificateOrg
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list orgs that have available certificates
        api_response = api_instance.list_cert_orgs(org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->list_cert_orgs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListTrustedCertificateOrg**](ListTrustedCertificateOrg.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list TrustedCertificateOrg |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_labels**
> ListTrustedCertificateLabel list_labels()

list TrustedCertificateLabel

List TrustedCertificateLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.list_trusted_certificate_label import ListTrustedCertificateLabel
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list TrustedCertificateLabel
        api_response = api_instance.list_labels(limit=limit, org_id=org_id, label=label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->list_labels: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]

### Return type

[**ListTrustedCertificateLabel**](ListTrustedCertificateLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of TrustedCertificateLabel |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_trusted_certs**
> ListTrustedCertificate list_trusted_certs()

list certificates

List certificates 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.list_trusted_certificate import ListTrustedCertificate
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    trusted_cert_label = TrustedCertificateLabelName("["example"]") # TrustedCertificateLabelName | Query TrustedCertificates with a matching label name (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    subject = "example" # str | Query a certificate based on subject name. This is an exact match query.  (optional)
    subject_search = "example" # str | Query a certificate based on subject name. Query for any certificates which contain this value as a case insensitive substring  (optional)
    subject_sha1 = "example" # str | Query a certificate based on the subject name sha128  (optional)
    subject_sha256 = "example" # str | Query a certificate based on the subject name sha256  (optional)
    cert_issuer = "example" # str | Query a certificate based on the issuer.  (optional)
    cert_issuer_search = "example" # str | Query a certificate based on the issuer Query for any certificates which contain this value as a case insensitive substring  (optional)
    serial_number = "example" # str | Query a certificate based on the serial number  (optional)
    skid = "example" # str | Query a certificate based on the subject key identifier  (optional)
    public_key_sha1 = "example" # str | Query a certificate based on the public key sha128  (optional)
    public_key_sha256 = "example" # str | Query a certificate based on the public key sha256  (optional)
    cert_root = True # bool | Query a certificates that are designated as a root  (optional)
    key_usage_extension_search = "key_usage_extension_search_example" # str | Query a certificates that have a matching key_usage_extension string. Query for any certificates which contain this value as a case insensitive substring  (optional)
    key_usage_crl_sign = True # bool | Query certificates that have key usage crl_sign  (optional)
    key_usage_key_cert_sign = True # bool | Query certificates that have key usage key_cert_sign  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list certificates
        api_response = api_instance.list_trusted_certs(limit=limit, org_id=org_id, trusted_cert_label=trusted_cert_label, page_at_id=page_at_id, subject=subject, subject_search=subject_search, subject_sha1=subject_sha1, subject_sha256=subject_sha256, cert_issuer=cert_issuer, cert_issuer_search=cert_issuer_search, serial_number=serial_number, skid=skid, public_key_sha1=public_key_sha1, public_key_sha256=public_key_sha256, cert_root=cert_root, key_usage_extension_search=key_usage_extension_search, key_usage_crl_sign=key_usage_crl_sign, key_usage_key_cert_sign=key_usage_key_cert_sign)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->list_trusted_certs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **trusted_cert_label** | **TrustedCertificateLabelName**| Query TrustedCertificates with a matching label name | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **subject** | **str**| Query a certificate based on subject name. This is an exact match query.  | [optional]
 **subject_search** | **str**| Query a certificate based on subject name. Query for any certificates which contain this value as a case insensitive substring  | [optional]
 **subject_sha1** | **str**| Query a certificate based on the subject name sha128  | [optional]
 **subject_sha256** | **str**| Query a certificate based on the subject name sha256  | [optional]
 **cert_issuer** | **str**| Query a certificate based on the issuer.  | [optional]
 **cert_issuer_search** | **str**| Query a certificate based on the issuer Query for any certificates which contain this value as a case insensitive substring  | [optional]
 **serial_number** | **str**| Query a certificate based on the serial number  | [optional]
 **skid** | **str**| Query a certificate based on the subject key identifier  | [optional]
 **public_key_sha1** | **str**| Query a certificate based on the public key sha128  | [optional]
 **public_key_sha256** | **str**| Query a certificate based on the public key sha256  | [optional]
 **cert_root** | **bool**| Query a certificates that are designated as a root  | [optional]
 **key_usage_extension_search** | **str**| Query a certificates that have a matching key_usage_extension string. Query for any certificates which contain this value as a case insensitive substring  | [optional]
 **key_usage_crl_sign** | **bool**| Query certificates that have key usage crl_sign  | [optional]
 **key_usage_key_cert_sign** | **bool**| Query certificates that have key usage key_cert_sign  | [optional]

### Return type

[**ListTrustedCertificate**](ListTrustedCertificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of TrustedCertificate |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_bundle**
> TrustedCertificateBundle replace_bundle(bundle, trusted_certificate_bundle)

Update a TrustedCertificateBundle

Update a TrustedCertificateBundle 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate_bundle import TrustedCertificateBundle
from agilicus_api.model.error_message import ErrorMessage
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    bundle = TrustedCertificateBundleName("1234") # TrustedCertificateBundleName | A TrustedCertificateBundleName
    trusted_certificate_bundle = TrustedCertificateBundle(
        metadata=MetadataWithId(),
        spec=TrustedCertificateBundleSpec(
            name=TrustedCertificateBundleName("0"),
            org_id="123",
            labels=[
                TrustedCertificateBundleLabel(
                    exclude=True,
                    label=TrustedCertificateLabelSpec(
                        name=TrustedCertificateLabelName("0"),
                        org_id="123",
                    ),
                ),
            ],
        ),
        status=TrustedCertificateBundleStatus(
            trusted_certs=[
                TrustedCertificate(
                    metadata=MetadataWithId(),
                    spec=TrustedCertificateSpec(
                        root=False,
                        certificate="certificate_example",
                        org_id="123",
                        labels=[
                            TrustedCertificateLabelName("labels_example"),
                        ],
                    ),
                    status=TrustedCertificateStatus(
                    ),
                ),
            ],
            trusted_certs_etag="trusted_certs_etag_example",
        ),
    ) # TrustedCertificateBundle | 

    # example passing only required values which don't have defaults set
    try:
        # Update a TrustedCertificateBundle
        api_response = api_instance.replace_bundle(bundle, trusted_certificate_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->replace_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bundle** | **TrustedCertificateBundleName**| A TrustedCertificateBundleName |
 **trusted_certificate_bundle** | [**TrustedCertificateBundle**](TrustedCertificateBundle.md)|  |

### Return type

[**TrustedCertificateBundle**](TrustedCertificateBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | TrustedCertificateBundle udpated |  -  |
**400** | The contents of the request body are invalid |  -  |
**409** | bundle name already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_trusted_cert**
> TrustedCertificate replace_trusted_cert(certificate_id, trusted_certificate)

Update a TrustedCertificate

Update a TrustedCertificate 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import trusted_certs_api
from agilicus_api.model.trusted_certificate import TrustedCertificate
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
    api_instance = trusted_certs_api.TrustedCertsApi(api_client)
    certificate_id = "1234" # str | A certificate id
    trusted_certificate = TrustedCertificate(
        metadata=MetadataWithId(),
        spec=TrustedCertificateSpec(
            root=False,
            certificate="certificate_example",
            org_id="123",
            labels=[
                TrustedCertificateLabelName("labels_example"),
            ],
        ),
        status=TrustedCertificateStatus(
        ),
    ) # TrustedCertificate | 

    # example passing only required values which don't have defaults set
    try:
        # Update a TrustedCertificate
        api_response = api_instance.replace_trusted_cert(certificate_id, trusted_certificate)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TrustedCertsApi->replace_trusted_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_id** | **str**| A certificate id |
 **trusted_certificate** | [**TrustedCertificate**](TrustedCertificate.md)|  |

### Return type

[**TrustedCertificate**](TrustedCertificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | TrustedCertificate updated. |  -  |
**400** | The contents of the request body are invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

