# agilicus_api.CredentialsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_object_credential**](CredentialsApi.md#create_object_credential) | **POST** /v1/object_credentials | Add an object_credential
[**delete_object_credential**](CredentialsApi.md#delete_object_credential) | **DELETE** /v1/object_credentials/{object_credential_id} | Delete an object_credential
[**get_object_credential**](CredentialsApi.md#get_object_credential) | **GET** /v1/object_credentials/{object_credential_id} | Get an object_credential
[**list_object_credential_existence_info**](CredentialsApi.md#list_object_credential_existence_info) | **GET** /v1/object_credentials/existence_info | List ObjectCredentialExistenceInfo
[**list_object_credentials**](CredentialsApi.md#list_object_credentials) | **GET** /v1/object_credentials | List all object_credentials
[**replace_object_credential**](CredentialsApi.md#replace_object_credential) | **PUT** /v1/object_credentials/{object_credential_id} | update an object_credential


# **create_object_credential**
> ObjectCredential create_object_credential(object_credential)

Add an object_credential

Adds an object_credential. Multiple credentials for a given purpose may exist for an object within an org. However, they must be distringuished by their priority. If one already exists for a given priority, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.object_credential import ObjectCredential
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
    api_instance = credentials_api.CredentialsApi(api_client)
    object_credential = ObjectCredential(
        metadata=MetadataWithId(),
        spec=ObjectCredentialSpec(
            object_id="123",
            object_type=ObjectType("desktop"),
            org_id="123",
            purpose=CredentialPurpose("H"),
            priority=0,
            secrets=ObjectCredentialSecrets(
                encrypt=False,
                encryption_key_id="cec712064d09e0902373cf7115c8e95befaa958d9252e0f333d9306969a19f45",
                username="my-username",
                private_key='''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABBJY2b4/q
bjyvhf8l69OU9bAAAAEAAAAAEAAABoAAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlz
dHAyNTYAAABBBIaysEbyyT6rKfzRnqh9wWR1TB6oX2v3tw0slZVaZ4drtlhS3b5Owk0tGE
zkCpoR2lpiQMcuVvM8wvyAme3MG2EAAACwK8Np7F7tZkOViQrQpIUjP52pXAuU88KoOCPA
XMRpsHeN71QmnzpWmSlFN1ePmYa2k+akfx6h7iDol9NFDppkN3K95W8y2JXIv4lcZ//jBQ
RVrkwtfAUxa6rwkoT0CGKoEOgChuk02E2fvoiYKD/eQ+koels17FZglTO4c25IQ6Zk4QzQ
YmijJ3BkZwfB4GR6nncUB7+PH3u5O4LmHca5YxoDLA3Mf7JSKm6NheyCuu4=
-----END OPENSSH PRIVATE KEY-----
''',
                private_key_passphrase="This is a long and random string you could never, ever guess.",
                password="9462#M@h+&g:",
            ),
            description="Used for accessing my super secret host",
        ),
        status=ObjectCredentialStatus(
            is_encrypted=True,
            encryption_key_id="cec712064d09e0902373cf7115c8e95befaa958d9252e0f333d9306969a19f45",
            username='YQ==',
            private_key='YQ==',
            private_key_passphrase='YQ==',
            password='YQ==',
        ),
    ) # ObjectCredential | 

    # example passing only required values which don't have defaults set
    try:
        # Add an object_credential
        api_response = api_instance.create_object_credential(object_credential)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->create_object_credential: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_credential** | [**ObjectCredential**](ObjectCredential.md)|  |

### Return type

[**ObjectCredential**](ObjectCredential.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New object_credential created. |  -  |
**400** | The request is invalid |  -  |
**409** | object_credential already exists. The existing label is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_object_credential**
> delete_object_credential(object_credential_id)

Delete an object_credential

Delete an object_credential

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
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
    api_instance = credentials_api.CredentialsApi(api_client)
    object_credential_id = "x9x7aD" # str | A credential ID
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete an object_credential
        api_instance.delete_object_credential(object_credential_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->delete_object_credential: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete an object_credential
        api_instance.delete_object_credential(object_credential_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->delete_object_credential: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_credential_id** | **str**| A credential ID |
 **org_id** | **str**| Organisation Unique identifier | [optional]

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
**204** | ObjectCredential was deleted |  -  |
**404** | ObjectCredential does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_object_credential**
> ObjectCredential get_object_credential(object_credential_id)

Get an object_credential

Get an object_credential

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.object_credential import ObjectCredential
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
    api_instance = credentials_api.CredentialsApi(api_client)
    object_credential_id = "x9x7aD" # str | A credential ID
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an object_credential
        api_response = api_instance.get_object_credential(object_credential_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->get_object_credential: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an object_credential
        api_response = api_instance.get_object_credential(object_credential_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->get_object_credential: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_credential_id** | **str**| A credential ID |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ObjectCredential**](ObjectCredential.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return an objectCredential |  -  |
**404** | ObjectCredential does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_object_credential_existence_info**
> ListObjectCredentialExistenceInfoResponse list_object_credential_existence_info()

List ObjectCredentialExistenceInfo

List whether or not ObjectCredentials exist for the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
from agilicus_api.model.credential_purpose import CredentialPurpose
from agilicus_api.model.list_object_credential_existence_info_response import ListObjectCredentialExistenceInfoResponse
from agilicus_api.model.object_type import ObjectType
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
    api_instance = credentials_api.CredentialsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    object_id = "1234" # str | search by object id (optional)
    object_type = ObjectType("abA12") # ObjectType | An object type (optional)
    object_types = [
        ObjectType("["abA12"]"),
    ] # [ObjectType] | A list of object types. Returns all items which match at least one of the types.  (optional)
    object_ids = ["aba23"] # [str] | A list of object IDs. Returns all items which match at least one of the .  (optional)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    purpose = CredentialPurpose("stuffing") # CredentialPurpose | The purpose of a credential (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List ObjectCredentialExistenceInfo
        api_response = api_instance.list_object_credential_existence_info(limit=limit, object_id=object_id, object_type=object_type, object_types=object_types, object_ids=object_ids, org_ids=org_ids, page_at_id=page_at_id, purpose=purpose, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->list_object_credential_existence_info: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **object_id** | **str**| search by object id | [optional]
 **object_type** | **ObjectType**| An object type | [optional]
 **object_types** | [**[ObjectType]**](ObjectType.md)| A list of object types. Returns all items which match at least one of the types.  | [optional]
 **object_ids** | **[str]**| A list of object IDs. Returns all items which match at least one of the .  | [optional]
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **purpose** | **CredentialPurpose**| The purpose of a credential | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListObjectCredentialExistenceInfoResponse**](ListObjectCredentialExistenceInfoResponse.md)

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

# **list_object_credentials**
> ListObjectCredentialsResponse list_object_credentials()

List all object_credentials

List all object_credentials matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
from agilicus_api.model.credential_purpose import CredentialPurpose
from agilicus_api.model.list_object_credentials_response import ListObjectCredentialsResponse
from agilicus_api.model.object_type import ObjectType
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
    api_instance = credentials_api.CredentialsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    object_id = "1234" # str | search by object id (optional)
    object_type = ObjectType("abA12") # ObjectType | An object type (optional)
    object_types = [
        ObjectType("["abA12"]"),
    ] # [ObjectType] | A list of object types. Returns all items which match at least one of the types.  (optional)
    object_ids = ["aba23"] # [str] | A list of object IDs. Returns all items which match at least one of the .  (optional)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    encryption_key_id = "1234" # str | query by the id of the key used to encrypt something (optional)
    purpose = CredentialPurpose("stuffing") # CredentialPurpose | The purpose of a credential (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all object_credentials
        api_response = api_instance.list_object_credentials(limit=limit, object_id=object_id, object_type=object_type, object_types=object_types, object_ids=object_ids, org_ids=org_ids, page_at_id=page_at_id, encryption_key_id=encryption_key_id, purpose=purpose, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->list_object_credentials: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **object_id** | **str**| search by object id | [optional]
 **object_type** | **ObjectType**| An object type | [optional]
 **object_types** | [**[ObjectType]**](ObjectType.md)| A list of object types. Returns all items which match at least one of the types.  | [optional]
 **object_ids** | **[str]**| A list of object IDs. Returns all items which match at least one of the .  | [optional]
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **encryption_key_id** | **str**| query by the id of the key used to encrypt something | [optional]
 **purpose** | **CredentialPurpose**| The purpose of a credential | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListObjectCredentialsResponse**](ListObjectCredentialsResponse.md)

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

# **replace_object_credential**
> ObjectCredential replace_object_credential(object_credential_id)

update an object_credential

update an object_credential

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import credentials_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.object_credential import ObjectCredential
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
    api_instance = credentials_api.CredentialsApi(api_client)
    object_credential_id = "x9x7aD" # str | A credential ID
    object_credential = ObjectCredential(
        metadata=MetadataWithId(),
        spec=ObjectCredentialSpec(
            object_id="123",
            object_type=ObjectType("desktop"),
            org_id="123",
            purpose=CredentialPurpose("H"),
            priority=0,
            secrets=ObjectCredentialSecrets(
                encrypt=False,
                encryption_key_id="cec712064d09e0902373cf7115c8e95befaa958d9252e0f333d9306969a19f45",
                username="my-username",
                private_key='''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABBJY2b4/q
bjyvhf8l69OU9bAAAAEAAAAAEAAABoAAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlz
dHAyNTYAAABBBIaysEbyyT6rKfzRnqh9wWR1TB6oX2v3tw0slZVaZ4drtlhS3b5Owk0tGE
zkCpoR2lpiQMcuVvM8wvyAme3MG2EAAACwK8Np7F7tZkOViQrQpIUjP52pXAuU88KoOCPA
XMRpsHeN71QmnzpWmSlFN1ePmYa2k+akfx6h7iDol9NFDppkN3K95W8y2JXIv4lcZ//jBQ
RVrkwtfAUxa6rwkoT0CGKoEOgChuk02E2fvoiYKD/eQ+koels17FZglTO4c25IQ6Zk4QzQ
YmijJ3BkZwfB4GR6nncUB7+PH3u5O4LmHca5YxoDLA3Mf7JSKm6NheyCuu4=
-----END OPENSSH PRIVATE KEY-----
''',
                private_key_passphrase="This is a long and random string you could never, ever guess.",
                password="9462#M@h+&g:",
            ),
            description="Used for accessing my super secret host",
        ),
        status=ObjectCredentialStatus(
            is_encrypted=True,
            encryption_key_id="cec712064d09e0902373cf7115c8e95befaa958d9252e0f333d9306969a19f45",
            username='YQ==',
            private_key='YQ==',
            private_key_passphrase='YQ==',
            password='YQ==',
        ),
    ) # ObjectCredential |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update an object_credential
        api_response = api_instance.replace_object_credential(object_credential_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->replace_object_credential: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update an object_credential
        api_response = api_instance.replace_object_credential(object_credential_id, object_credential=object_credential)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling CredentialsApi->replace_object_credential: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_credential_id** | **str**| A credential ID |
 **object_credential** | [**ObjectCredential**](ObjectCredential.md)|  | [optional]

### Return type

[**ObjectCredential**](ObjectCredential.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated ObjectCredential |  -  |
**400** | The request is invalid |  -  |
**404** | ObjectCredential does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

