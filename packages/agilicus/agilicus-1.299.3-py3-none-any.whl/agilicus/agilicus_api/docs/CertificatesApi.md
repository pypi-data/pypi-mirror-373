# agilicus_api.CertificatesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_cert**](CertificatesApi.md#create_cert) | **POST** /v1/certificates | Creates a X509Certificate
[**create_cert_tracker**](CertificatesApi.md#create_cert_tracker) | **POST** /v1/certificate_trackers | Creates a CertificateTracker
[**create_cert_tracker_cert**](CertificatesApi.md#create_cert_tracker_cert) | **POST** /v1/certificate_trackers/{certificate_tracker_id}/certificates | Creates a X509Certificate associated to a CertificateTracker
[**delete_agent_csr**](CertificatesApi.md#delete_agent_csr) | **DELETE** /v1/agent_connectors/{connector_id}/certificate_signing_requests/{csr_id} | Delete a CertSigningReq
[**delete_cert**](CertificatesApi.md#delete_cert) | **DELETE** /v1/certificates/{certificate_id} | Delete a X509Certificate
[**delete_cert_tracker**](CertificatesApi.md#delete_cert_tracker) | **DELETE** /v1/certificate_trackers/{certificate_tracker_id} | Delete a CertificateTracker
[**delete_csr**](CertificatesApi.md#delete_csr) | **DELETE** /v1/certificate_signing_requests/{csr_id} | Delete a CertSigningReq
[**get_cert**](CertificatesApi.md#get_cert) | **GET** /v1/certificates/{certificate_id} | Get a X509Certificate
[**get_cert_tracker**](CertificatesApi.md#get_cert_tracker) | **GET** /v1/certificate_trackers/{certificate_tracker_id} | Get a CertificateTracker
[**get_csr**](CertificatesApi.md#get_csr) | **GET** /v1/certificate_signing_requests/{csr_id} | Get a CertSigningReq
[**list_cert_trackers**](CertificatesApi.md#list_cert_trackers) | **GET** /v1/certificate_trackers | list certificate trackers
[**list_certs**](CertificatesApi.md#list_certs) | **GET** /v1/certificates | list certificates
[**list_csr**](CertificatesApi.md#list_csr) | **GET** /v1/certificate_signing_requests | list certificate signing requests
[**list_root_certs**](CertificatesApi.md#list_root_certs) | **GET** /v1/root_certificates | list root certificates
[**reissue_cert_for_csr**](CertificatesApi.md#reissue_cert_for_csr) | **POST** /v1/certificate_signing_requests/reissue | Creates a CertSigningRequestReissue
[**replace_cert_tracker**](CertificatesApi.md#replace_cert_tracker) | **PUT** /v1/certificate_trackers/{certificate_tracker_id} | Update a CertificateTracker
[**replace_csr**](CertificatesApi.md#replace_csr) | **PUT** /v1/certificate_signing_requests/{csr_id} | Update a CertSigningReq


# **create_cert**
> X509Certificate create_cert(x509_certificate)

Creates a X509Certificate

Creates a X509Certificate 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.x509_certificate import X509Certificate
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
    api_instance = certificates_api.CertificatesApi(api_client)
    x509_certificate = X509Certificate(
        metadata=MetadataWithId(),
        spec=X509CertificateSpec(
            ca="ca_example",
            certificate="certificate_example",
            encryption_key_id="encryption_key_id_example",
            encrypted_priv_key="encrypted_priv_key_example",
            csr_id="csr_id_example",
            org_id="123",
            message="message_example",
            reason=CSRReasonEnum("pending"),
            certificate_tracker_id="certificate_tracker_id_example",
        ),
        status=X509CertificateStatus(
        ),
    ) # X509Certificate | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a X509Certificate
        api_response = api_instance.create_cert(x509_certificate)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->create_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x509_certificate** | [**X509Certificate**](X509Certificate.md)|  |

### Return type

[**X509Certificate**](X509Certificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | X509Certificate created and returned. |  -  |
**404** | CertSigningReq does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cert_tracker**
> CertificateTracker create_cert_tracker(certificate_tracker)

Creates a CertificateTracker

Creates a CertificateTracker 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.certificate_tracker import CertificateTracker
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_tracker = CertificateTracker(
        metadata=MetadataWithId(),
        spec=CertificateTrackerSpec(
            org_id="org_id_example",
            config=CertificateTrackerConfig(
                dns_names=[
                    Domain("dns_names_example"),
                ],
                label="label_example",
            ),
            uid="uid_example",
            max_certificate_history=3,
        ),
        status=CertificateTrackerStatus(
            certificates=[
                X509Certificate(
                    metadata=MetadataWithId(),
                    spec=X509CertificateSpec(
                        ca="ca_example",
                        certificate="certificate_example",
                        encryption_key_id="encryption_key_id_example",
                        encrypted_priv_key="encrypted_priv_key_example",
                        csr_id="csr_id_example",
                        org_id="123",
                        message="message_example",
                        reason=CSRReasonEnum("pending"),
                        certificate_tracker_id="certificate_tracker_id_example",
                    ),
                    status=X509CertificateStatus(
                    ),
                ),
            ],
        ),
    ) # CertificateTracker | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a CertificateTracker
        api_response = api_instance.create_cert_tracker(certificate_tracker)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->create_cert_tracker: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_tracker** | [**CertificateTracker**](CertificateTracker.md)|  |

### Return type

[**CertificateTracker**](CertificateTracker.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | CertificateTracker created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_cert_tracker_cert**
> X509Certificate create_cert_tracker_cert(certificate_tracker_id, x509_certificate)

Creates a X509Certificate associated to a CertificateTracker

Creates a X509Certificate associated to a CertificateTracker 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.x509_certificate import X509Certificate
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_tracker_id = "1234" # str | A certificate tracker id
    x509_certificate = X509Certificate(
        metadata=MetadataWithId(),
        spec=X509CertificateSpec(
            ca="ca_example",
            certificate="certificate_example",
            encryption_key_id="encryption_key_id_example",
            encrypted_priv_key="encrypted_priv_key_example",
            csr_id="csr_id_example",
            org_id="123",
            message="message_example",
            reason=CSRReasonEnum("pending"),
            certificate_tracker_id="certificate_tracker_id_example",
        ),
        status=X509CertificateStatus(
        ),
    ) # X509Certificate | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a X509Certificate associated to a CertificateTracker
        api_response = api_instance.create_cert_tracker_cert(certificate_tracker_id, x509_certificate)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->create_cert_tracker_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_tracker_id** | **str**| A certificate tracker id |
 **x509_certificate** | [**X509Certificate**](X509Certificate.md)|  |

### Return type

[**X509Certificate**](X509Certificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | X509Certificate created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_agent_csr**
> delete_agent_csr(connector_id, csr_id)

Delete a CertSigningReq

Delete a CertSigningReq

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
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
    api_instance = certificates_api.CertificatesApi(api_client)
    connector_id = "1234" # str | connector id path
    csr_id = "1234" # str | A certificate signing request id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a CertSigningReq
        api_instance.delete_agent_csr(connector_id, csr_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_agent_csr: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a CertSigningReq
        api_instance.delete_agent_csr(connector_id, csr_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_agent_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connector_id** | **str**| connector id path |
 **csr_id** | **str**| A certificate signing request id |
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
**204** | CertSigningReq was deleted |  -  |
**404** | CertSigningReq does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cert**
> delete_cert(certificate_id)

Delete a X509Certificate

Delete a X509Certificate

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_id = "1234" # str | A certificate id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a X509Certificate
        api_instance.delete_cert(certificate_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_cert: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a X509Certificate
        api_instance.delete_cert(certificate_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_cert: %s\n" % e)
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
**204** | X509Certificate was deleted |  -  |
**404** | X509Certificate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cert_tracker**
> delete_cert_tracker(certificate_tracker_id)

Delete a CertificateTracker

Delete a CertificateTracker

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_tracker_id = "1234" # str | A certificate tracker id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a CertificateTracker
        api_instance.delete_cert_tracker(certificate_tracker_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_cert_tracker: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a CertificateTracker
        api_instance.delete_cert_tracker(certificate_tracker_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_cert_tracker: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_tracker_id** | **str**| A certificate tracker id |
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
**204** | CertificateTracker was deleted |  -  |
**404** | CertificateTracker does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_csr**
> delete_csr(csr_id)

Delete a CertSigningReq

Delete a CertSigningReq

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
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
    api_instance = certificates_api.CertificatesApi(api_client)
    csr_id = "1234" # str | A certificate signing request id
    org_id = "1234" # str | Organisation Unique identifier (optional)
    private_key_id = "1234" # str | query by private key id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a CertSigningReq
        api_instance.delete_csr(csr_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_csr: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a CertSigningReq
        api_instance.delete_csr(csr_id, org_id=org_id, private_key_id=private_key_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->delete_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csr_id** | **str**| A certificate signing request id |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **private_key_id** | **str**| query by private key id | [optional]

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
**204** | CertSigningReq was deleted |  -  |
**404** | CertSigningReq does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cert**
> X509Certificate get_cert(certificate_id)

Get a X509Certificate

Get a X509Certificate

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.x509_certificate import X509Certificate
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_id = "1234" # str | A certificate id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a X509Certificate
        api_response = api_instance.get_cert(certificate_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_cert: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a X509Certificate
        api_response = api_instance.get_cert(certificate_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_cert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_id** | **str**| A certificate id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**X509Certificate**](X509Certificate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | X509Certificate found and returned |  -  |
**404** | X509Certificate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cert_tracker**
> CertificateTracker get_cert_tracker(certificate_tracker_id)

Get a CertificateTracker

Get a CertificateTracker

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.certificate_tracker import CertificateTracker
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_tracker_id = "1234" # str | A certificate tracker id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a CertificateTracker
        api_response = api_instance.get_cert_tracker(certificate_tracker_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_cert_tracker: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a CertificateTracker
        api_response = api_instance.get_cert_tracker(certificate_tracker_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_cert_tracker: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_tracker_id** | **str**| A certificate tracker id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**CertificateTracker**](CertificateTracker.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertificateTracker found and returned |  -  |
**404** | CertificateTracker does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_csr**
> CertSigningReq get_csr(csr_id)

Get a CertSigningReq

Get a CertSigningReq

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.cert_signing_req import CertSigningReq
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
    api_instance = certificates_api.CertificatesApi(api_client)
    csr_id = "1234" # str | A certificate signing request id
    org_id = "1234" # str | Organisation Unique identifier (optional)
    private_key_id = "1234" # str | query by private key id (optional)
    limit_csr_certificates = 1 # int | limit the number of certficates returned in a csr (optional) if omitted the server will use the default value of 10
    get_certificate_updates = False # bool | For CSR queries, also return certificate updates for pending or failed certificates. (optional) if omitted the server will use the default value of False
    certificate_updates_start_cursor = 0 # int | If get_certificate_updates is enabled, specifies the starting point cursor query. (optional) if omitted the server will use the default value of 0
    certificate_updates_end_cursor = 99 # int | If get_certificate_updates is enabled, specifies the end of the query range (starting with certificate_updates_start_cursor). (optional) if omitted the server will use the default value of 99

    # example passing only required values which don't have defaults set
    try:
        # Get a CertSigningReq
        api_response = api_instance.get_csr(csr_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_csr: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a CertSigningReq
        api_response = api_instance.get_csr(csr_id, org_id=org_id, private_key_id=private_key_id, limit_csr_certificates=limit_csr_certificates, get_certificate_updates=get_certificate_updates, certificate_updates_start_cursor=certificate_updates_start_cursor, certificate_updates_end_cursor=certificate_updates_end_cursor)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->get_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csr_id** | **str**| A certificate signing request id |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **private_key_id** | **str**| query by private key id | [optional]
 **limit_csr_certificates** | **int**| limit the number of certficates returned in a csr | [optional] if omitted the server will use the default value of 10
 **get_certificate_updates** | **bool**| For CSR queries, also return certificate updates for pending or failed certificates. | [optional] if omitted the server will use the default value of False
 **certificate_updates_start_cursor** | **int**| If get_certificate_updates is enabled, specifies the starting point cursor query. | [optional] if omitted the server will use the default value of 0
 **certificate_updates_end_cursor** | **int**| If get_certificate_updates is enabled, specifies the end of the query range (starting with certificate_updates_start_cursor). | [optional] if omitted the server will use the default value of 99

### Return type

[**CertSigningReq**](CertSigningReq.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertSigningReq found and returned |  -  |
**404** | CertSigningReq does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_cert_trackers**
> ListCertificateTrackerResponse list_cert_trackers()

list certificate trackers

List certificate trackers 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.list_certificate_tracker_response import ListCertificateTrackerResponse
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
    api_instance = certificates_api.CertificatesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list certificate trackers
        api_response = api_instance.list_cert_trackers(limit=limit, org_id=org_id, page_at_id=page_at_id, org_ids=org_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->list_cert_trackers: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]

### Return type

[**ListCertificateTrackerResponse**](ListCertificateTrackerResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of CertificateTracker |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_certs**
> ListX509CertificateResponse list_certs()

list certificates

List certificates 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.list_x509_certificate_response import ListX509CertificateResponse
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
    api_instance = certificates_api.CertificatesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list certificates
        api_response = api_instance.list_certs(limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->list_certs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListX509CertificateResponse**](ListX509CertificateResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of X509Certificate |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_csr**
> ListCertSigningReqResponse list_csr()

list certificate signing requests

List certificate signing requests. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.list_cert_signing_req_response import ListCertSigningReqResponse
from agilicus_api.model.csr_reason_enum import CSRReasonEnum
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
    api_instance = certificates_api.CertificatesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    reason = CSRReasonEnum("pending") # CSRReasonEnum | Query a CSR based on its certificate reason status. This option is deprecated, as all csr queries will return only issued certificates.  (optional)
    not_valid_after = "in 30 days" # str | Search criteria for finding expired certificates * In UTC. * Supports human-friendly values. * Example, find all expired certificates in 30 days: not_after_after=\"in 30 days\" * Example, find all expired certificates today:  not_valid_after=\"tomorrow\" * Example, find all expired now:  not_valid_after=\"now\"  (optional)
    target_issuer = [
        "agilicus-private",
    ] # [str] | A list of target issuers to search for. If an item matches an entry in the list, is returned.  (optional)
    limit_csr_certificates = 1 # int | limit the number of certficates returned in a csr (optional) if omitted the server will use the default value of 10
    get_certificate_updates = False # bool | For CSR queries, also return certificate updates for pending or failed certificates. (optional) if omitted the server will use the default value of False
    certificate_updates_start_cursor = 0 # int | If get_certificate_updates is enabled, specifies the starting point cursor query. (optional) if omitted the server will use the default value of 0
    certificate_updates_end_cursor = 99 # int | If get_certificate_updates is enabled, specifies the end of the query range (starting with certificate_updates_start_cursor). (optional) if omitted the server will use the default value of 99
    auto_renew = True # bool | When enabled, query only certificate requests that have their auto_renew status enabled, when false, query only certificate requests that have their auto_renew as false. If not set (neither true or false), certificate requests are returned regardless of the auto_renew status.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list certificate signing requests
        api_response = api_instance.list_csr(limit=limit, org_id=org_id, reason=reason, not_valid_after=not_valid_after, target_issuer=target_issuer, limit_csr_certificates=limit_csr_certificates, get_certificate_updates=get_certificate_updates, certificate_updates_start_cursor=certificate_updates_start_cursor, certificate_updates_end_cursor=certificate_updates_end_cursor, auto_renew=auto_renew)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->list_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **reason** | **CSRReasonEnum**| Query a CSR based on its certificate reason status. This option is deprecated, as all csr queries will return only issued certificates.  | [optional]
 **not_valid_after** | **str**| Search criteria for finding expired certificates * In UTC. * Supports human-friendly values. * Example, find all expired certificates in 30 days: not_after_after&#x3D;\&quot;in 30 days\&quot; * Example, find all expired certificates today:  not_valid_after&#x3D;\&quot;tomorrow\&quot; * Example, find all expired now:  not_valid_after&#x3D;\&quot;now\&quot;  | [optional]
 **target_issuer** | **[str]**| A list of target issuers to search for. If an item matches an entry in the list, is returned.  | [optional]
 **limit_csr_certificates** | **int**| limit the number of certficates returned in a csr | [optional] if omitted the server will use the default value of 10
 **get_certificate_updates** | **bool**| For CSR queries, also return certificate updates for pending or failed certificates. | [optional] if omitted the server will use the default value of False
 **certificate_updates_start_cursor** | **int**| If get_certificate_updates is enabled, specifies the starting point cursor query. | [optional] if omitted the server will use the default value of 0
 **certificate_updates_end_cursor** | **int**| If get_certificate_updates is enabled, specifies the end of the query range (starting with certificate_updates_start_cursor). | [optional] if omitted the server will use the default value of 99
 **auto_renew** | **bool**| When enabled, query only certificate requests that have their auto_renew status enabled, when false, query only certificate requests that have their auto_renew as false. If not set (neither true or false), certificate requests are returned regardless of the auto_renew status.  | [optional]

### Return type

[**ListCertSigningReqResponse**](ListCertSigningReqResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of CertSigningReq |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_root_certs**
> InlineResponse200 list_root_certs()

list root certificates

List the root certificates an organsation should trust when interacting with the local resources exposed by the Agilicus platform. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.inline_response200 import InlineResponse200
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
    api_instance = certificates_api.CertificatesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list root certificates
        api_response = api_instance.list_root_certs(limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->list_root_certs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The matching list of X509RootCertificate items. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reissue_cert_for_csr**
> CertSigningReqReissue reissue_cert_for_csr(cert_signing_req_reissue)

Creates a CertSigningRequestReissue

Creates a CertSigningReqReissue. This procedure uses the old_not_after_time to ensure that only one certificate request can be created in a given time period. Clients can coordinate to limit the number of issued certificates by setting the old_not_after_time to the not_after_time of the most recently issued certificate. CConcurrent requests to reissue based off the same certificate will lead to only one certificate being created. This will fail if the old_not_after_time is equal to the recently used old_not_after_time as part of that coordination. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.cert_signing_req_reissue import CertSigningReqReissue
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
    api_instance = certificates_api.CertificatesApi(api_client)
    cert_signing_req_reissue = CertSigningReqReissue(
        spec=CertSigningReqReissueSpec(
            org_id="123",
            csr_id="csr_id_example",
            old_not_after=dateutil_parser('1970-01-01T00:00:00.00Z'),
        ),
        status=CertSigningReqReissueStatus(
            new_certificate=X509Certificate(
                metadata=MetadataWithId(),
                spec=X509CertificateSpec(
                    ca="ca_example",
                    certificate="certificate_example",
                    encryption_key_id="encryption_key_id_example",
                    encrypted_priv_key="encrypted_priv_key_example",
                    csr_id="csr_id_example",
                    org_id="123",
                    message="message_example",
                    reason=CSRReasonEnum("pending"),
                    certificate_tracker_id="certificate_tracker_id_example",
                ),
                status=X509CertificateStatus(
                ),
            ),
        ),
    ) # CertSigningReqReissue | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a CertSigningRequestReissue
        api_response = api_instance.reissue_cert_for_csr(cert_signing_req_reissue)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->reissue_cert_for_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cert_signing_req_reissue** | [**CertSigningReqReissue**](CertSigningReqReissue.md)|  |

### Return type

[**CertSigningReqReissue**](CertSigningReqReissue.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Certificate creation started |  -  |
**404** | Correspondong CSR does not exist |  -  |
**409** | The request conflicted with another one. This usually happens if two clients simultaneously requested a reissuance.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_cert_tracker**
> CertificateTracker replace_cert_tracker(certificate_tracker_id)

Update a CertificateTracker

Update a CertificateTracker

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.certificate_tracker import CertificateTracker
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
    api_instance = certificates_api.CertificatesApi(api_client)
    certificate_tracker_id = "1234" # str | A certificate tracker id
    certificate_tracker = CertificateTracker(
        metadata=MetadataWithId(),
        spec=CertificateTrackerSpec(
            org_id="org_id_example",
            config=CertificateTrackerConfig(
                dns_names=[
                    Domain("dns_names_example"),
                ],
                label="label_example",
            ),
            uid="uid_example",
            max_certificate_history=3,
        ),
        status=CertificateTrackerStatus(
            certificates=[
                X509Certificate(
                    metadata=MetadataWithId(),
                    spec=X509CertificateSpec(
                        ca="ca_example",
                        certificate="certificate_example",
                        encryption_key_id="encryption_key_id_example",
                        encrypted_priv_key="encrypted_priv_key_example",
                        csr_id="csr_id_example",
                        org_id="123",
                        message="message_example",
                        reason=CSRReasonEnum("pending"),
                        certificate_tracker_id="certificate_tracker_id_example",
                    ),
                    status=X509CertificateStatus(
                    ),
                ),
            ],
        ),
    ) # CertificateTracker |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a CertificateTracker
        api_response = api_instance.replace_cert_tracker(certificate_tracker_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->replace_cert_tracker: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a CertificateTracker
        api_response = api_instance.replace_cert_tracker(certificate_tracker_id, certificate_tracker=certificate_tracker)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->replace_cert_tracker: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificate_tracker_id** | **str**| A certificate tracker id |
 **certificate_tracker** | [**CertificateTracker**](CertificateTracker.md)|  | [optional]

### Return type

[**CertificateTracker**](CertificateTracker.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertificateTracker updated |  -  |
**400** | The contents of the request body are invalid |  -  |
**404** | CertificateTracker does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_csr**
> CertSigningReq replace_csr(csr_id)

Update a CertSigningReq

Update a CertSigningReq

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import certificates_api
from agilicus_api.model.cert_signing_req import CertSigningReq
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
    api_instance = certificates_api.CertificatesApi(api_client)
    csr_id = "1234" # str | A certificate signing request id
    org_id = "1234" # str | Organisation Unique identifier (optional)
    private_key_id = "1234" # str | query by private key id (optional)
    cert_signing_req = CertSigningReq(
        metadata=MetadataWithId(),
        spec=CertSigningReqSpec(
            org_id="123",
            auto_renew=True,
            rotate_keys=True,
            private_key_id="private_key_id_example",
            request="request_example",
            target_issuer="agilicus-private",
            uid="uid_example",
        ),
        status=CertSigningReqStatus(
            certificates=[
                X509Certificate(
                    metadata=MetadataWithId(),
                    spec=X509CertificateSpec(
                        ca="ca_example",
                        certificate="certificate_example",
                        encryption_key_id="encryption_key_id_example",
                        encrypted_priv_key="encrypted_priv_key_example",
                        csr_id="csr_id_example",
                        org_id="123",
                        message="message_example",
                        reason=CSRReasonEnum("pending"),
                        certificate_tracker_id="certificate_tracker_id_example",
                    ),
                    status=X509CertificateStatus(
                    ),
                ),
            ],
            connector_id="123",
            auto_renew=True,
            certificate_updates=[
                X509Certificate(
                    metadata=MetadataWithId(),
                    spec=X509CertificateSpec(
                        ca="ca_example",
                        certificate="certificate_example",
                        encryption_key_id="encryption_key_id_example",
                        encrypted_priv_key="encrypted_priv_key_example",
                        csr_id="csr_id_example",
                        org_id="123",
                        message="message_example",
                        reason=CSRReasonEnum("pending"),
                        certificate_tracker_id="certificate_tracker_id_example",
                    ),
                    status=X509CertificateStatus(
                    ),
                ),
            ],
        ),
    ) # CertSigningReq |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a CertSigningReq
        api_response = api_instance.replace_csr(csr_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->replace_csr: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a CertSigningReq
        api_response = api_instance.replace_csr(csr_id, org_id=org_id, private_key_id=private_key_id, cert_signing_req=cert_signing_req)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CertificatesApi->replace_csr: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csr_id** | **str**| A certificate signing request id |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **private_key_id** | **str**| query by private key id | [optional]
 **cert_signing_req** | [**CertSigningReq**](CertSigningReq.md)|  | [optional]

### Return type

[**CertSigningReq**](CertSigningReq.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CertSigningReq updated |  -  |
**400** | The contents of the request body are invalid |  -  |
**404** | csr does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

