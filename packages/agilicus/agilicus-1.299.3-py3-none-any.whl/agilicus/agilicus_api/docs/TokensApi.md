# agilicus_api.TokensApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_api_key**](TokensApi.md#create_api_key) | **POST** /v1/api_keys | Create an API Key
[**create_api_key_introspection**](TokensApi.md#create_api_key_introspection) | **POST** /v1/api_keys/introspect | Introspect an API Key
[**create_authentication_document**](TokensApi.md#create_authentication_document) | **POST** /v1/authentication_documents | Create a authentication document
[**create_bulk_delete_session_task**](TokensApi.md#create_bulk_delete_session_task) | **POST** /v1/sessions/bulk_delete | Delete a set of sessions
[**create_bulk_revoke_session_task**](TokensApi.md#create_bulk_revoke_session_task) | **POST** /v1/sessions/bulk_revoke | Revoke a set of sessions
[**create_bulk_revoke_token_task**](TokensApi.md#create_bulk_revoke_token_task) | **POST** /v1/tokens/bulk_revoke | Revoke a set of tokens
[**create_introspect_token**](TokensApi.md#create_introspect_token) | **POST** /v1/tokens/introspect | Introspect a token
[**create_introspect_token_all_sub_orgs**](TokensApi.md#create_introspect_token_all_sub_orgs) | **POST** /v1/tokens/introspect_all_sub_orgs | Introspect a token in all sub orgs
[**create_reissued_token**](TokensApi.md#create_reissued_token) | **POST** /v1/tokens/reissue | Issue a new token from another
[**create_revoke_token_task**](TokensApi.md#create_revoke_token_task) | **POST** /v1/tokens/revoke | Revoke a token
[**create_session**](TokensApi.md#create_session) | **POST** /v1/sessions | Create a session
[**create_session_and_token**](TokensApi.md#create_session_and_token) | **POST** /v1/sessions/create_session_and_token | Create a session and a token associated with the session
[**create_session_challenge**](TokensApi.md#create_session_challenge) | **POST** /v1/session_challenges | Create a user challenge request for a session
[**create_token**](TokensApi.md#create_token) | **POST** /v1/tokens | Create a token
[**create_token_validation**](TokensApi.md#create_token_validation) | **POST** /v1/tokens/validations | Validate a token request
[**create_user_data_token**](TokensApi.md#create_user_data_token) | **POST** /v1/user_data_tokens | Create a User Data Token
[**delete_api_key**](TokensApi.md#delete_api_key) | **DELETE** /v1/api_keys/{api_key_id} | Delete an API Key
[**delete_authentication_document**](TokensApi.md#delete_authentication_document) | **DELETE** /v1/authentication_documents/{document_id} | Delete a authentication document
[**delete_session**](TokensApi.md#delete_session) | **DELETE** /v1/sessions/{session_id} | Delete a session
[**get_api_key**](TokensApi.md#get_api_key) | **GET** /v1/api_keys/{api_key_id} | Get an API Key
[**get_authentication_document**](TokensApi.md#get_authentication_document) | **GET** /v1/authentication_documents/{document_id} | Get a authentication document
[**get_jwks**](TokensApi.md#get_jwks) | **GET** /v1/tokens/jwsk | Return JSON Web Key Set (JWKS)
[**get_session**](TokensApi.md#get_session) | **GET** /v1/sessions/{session_id} | Get a session
[**get_token**](TokensApi.md#get_token) | **GET** /v1/tokens/introspect_self | introspect token
[**get_user_data_jwks**](TokensApi.md#get_user_data_jwks) | **GET** /v1/user_data_tokens/jwks | Return JSON Web Key Set (JWKS)
[**list_api_keys**](TokensApi.md#list_api_keys) | **GET** /v1/api_keys | List API Keys
[**list_authentication_documents**](TokensApi.md#list_authentication_documents) | **GET** /v1/authentication_documents | List authentication documents
[**list_sessions**](TokensApi.md#list_sessions) | **GET** /v1/sessions | List Sessions
[**list_tokens**](TokensApi.md#list_tokens) | **GET** /v1/tokens | Query tokens
[**refresh_token**](TokensApi.md#refresh_token) | **POST** /v1/tokens/refresh | Refresh a token
[**replace_api_key**](TokensApi.md#replace_api_key) | **PUT** /v1/api_keys/{api_key_id} | Update an API key
[**replace_session**](TokensApi.md#replace_session) | **PUT** /v1/sessions/{session_id} | Update a session
[**update_session_challenge**](TokensApi.md#update_session_challenge) | **POST** /v1/session_challenges/update_session | Update a session with its challenge answer
[**validate_identity_assertion**](TokensApi.md#validate_identity_assertion) | **POST** /v1/authentication_documents_rpc/validate_identity_assertion | Validate an identity assertion


# **create_api_key**
> APIKey create_api_key(api_key)

Create an API Key

Creates an API Key with the provided body. Note that the secret which serves as the key to provide access is only available when the API Key is created. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.api_key import APIKey
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
    api_instance = tokens_api.TokensApi(api_client)
    api_key = APIKey(
        metadata=MetadataWithId(),
        spec=APIKeySpec(
            user_id="123",
            org_id="123",
            expiry=dateutil_parser('2002-10-02T10:00:00-05:00'),
            session="123",
            scopes=[
                TokenScope("urn:agilicus:users:owner"),
            ],
            name="my-tool-api-key",
            label="automated-share-access",
        ),
        status=APIKeyStatus(
            api_key="api_key_example",
            token_id="123",
            creating_sub="9Xd8s0d2kd",
            creating_org="5Xd8s0d2kd",
            masquerading=False,
            oper_status=APIKeyOpStatus("active"),
        ),
    ) # APIKey | 

    # example passing only required values which don't have defaults set
    try:
        # Create an API Key
        api_response = api_instance.create_api_key(api_key)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_api_key: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key** | [**APIKey**](APIKey.md)|  |

### Return type

[**APIKey**](APIKey.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New API Key |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_api_key_introspection**
> APIKeyIntrospectResponse create_api_key_introspection(api_key_introspect)

Introspect an API Key

Introspect an API Key to determine its permissions

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.api_key_introspect_response import APIKeyIntrospectResponse
from agilicus_api.model.api_key_introspect import APIKeyIntrospect
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    api_key_introspect = APIKeyIntrospect(
        api_key_auth_info=APIKeyIntrospectAuthorizationInfo(
            key="key_example",
            username="username_example",
        ),
        introspect_options=TokenIntrospectOptions(
            exclude_roles=False,
            support_http_matchers=True,
            target_org_info=OrgInfo(
                target_orgs=["org-1","org-2"],
                target_domain="app1.example.com",
            ),
            no_cache=False,
        ),
        multi_org=False,
    ) # APIKeyIntrospect | API Key to introspect

    # example passing only required values which don't have defaults set
    try:
        # Introspect an API Key
        api_response = api_instance.create_api_key_introspection(api_key_introspect)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_api_key_introspection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_introspect** | [**APIKeyIntrospect**](APIKeyIntrospect.md)| API Key to introspect |

### Return type

[**APIKeyIntrospectResponse**](APIKeyIntrospectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Introspection succeeded. |  -  |
**410** | The API Key has been revoked. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_authentication_document**
> AuthenticationDocument create_authentication_document(authentication_document)

Create a authentication document

Creates an authentication document with the provided body

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.authentication_document import AuthenticationDocument
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
    api_instance = tokens_api.TokensApi(api_client)
    authentication_document = AuthenticationDocument(
        metadata=MetadataWithId(),
        spec=AuthenticationDocumentSpec(
            user_id="asdfghjklmn123",
            org_id="asdfghjklmn123",
            auth_issuer_url="https://auth.cloud.egov.city",
            expiry=dateutil_parser('2002-10-02T10:00:00-05:00'),
        ),
    ) # AuthenticationDocument | 

    # example passing only required values which don't have defaults set
    try:
        # Create a authentication document
        api_response = api_instance.create_authentication_document(authentication_document)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_authentication_document: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authentication_document** | [**AuthenticationDocument**](AuthenticationDocument.md)|  |

### Return type

[**AuthenticationDocument**](AuthenticationDocument.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New authentication document |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_bulk_delete_session_task**
> BulkSessionOperationResponse create_bulk_delete_session_task(user_session_identifiers)

Delete a set of sessions

Delete a set of sessions. The body parameters determine the set of sessions

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.bulk_session_operation_response import BulkSessionOperationResponse
from agilicus_api.model.user_session_identifiers import UserSessionIdentifiers
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
    api_instance = tokens_api.TokensApi(api_client)
    user_session_identifiers = UserSessionIdentifiers(
        user_id="tuU7smH86zAXMl76sua6xQ",
        org_id="IAsl3dl40aSsfLKiU76",
        session_id="XAYl3dl40uSsfLViU76",
        tokens_only=True,
    ) # UserSessionIdentifiers | The identifying information for which sessions to delete

    # example passing only required values which don't have defaults set
    try:
        # Delete a set of sessions
        api_response = api_instance.create_bulk_delete_session_task(user_session_identifiers)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_bulk_delete_session_task: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_session_identifiers** | [**UserSessionIdentifiers**](UserSessionIdentifiers.md)| The identifying information for which sessions to delete |

### Return type

[**BulkSessionOperationResponse**](BulkSessionOperationResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | sessions have been deleted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_bulk_revoke_session_task**
> BulkSessionOperationResponse create_bulk_revoke_session_task(user_session_identifiers)

Revoke a set of sessions

Revoke a set of sessions. The body parameters determine the set of sessions

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.bulk_session_operation_response import BulkSessionOperationResponse
from agilicus_api.model.user_session_identifiers import UserSessionIdentifiers
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
    api_instance = tokens_api.TokensApi(api_client)
    user_session_identifiers = UserSessionIdentifiers(
        user_id="tuU7smH86zAXMl76sua6xQ",
        org_id="IAsl3dl40aSsfLKiU76",
        session_id="XAYl3dl40uSsfLViU76",
        tokens_only=True,
    ) # UserSessionIdentifiers | The identifying information for which sessions to revoke

    # example passing only required values which don't have defaults set
    try:
        # Revoke a set of sessions
        api_response = api_instance.create_bulk_revoke_session_task(user_session_identifiers)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_bulk_revoke_session_task: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_session_identifiers** | [**UserSessionIdentifiers**](UserSessionIdentifiers.md)| The identifying information for which sessions to revoke |

### Return type

[**BulkSessionOperationResponse**](BulkSessionOperationResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | sessions have been revoked |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_bulk_revoke_token_task**
> BulkTokenRevokeResponse create_bulk_revoke_token_task(bulk_token_revoke)

Revoke a set of tokens

Revoke a set of tokens. The body parameters determine the set of tokens

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.bulk_token_revoke import BulkTokenRevoke
from agilicus_api.model.bulk_token_revoke_response import BulkTokenRevokeResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    bulk_token_revoke = BulkTokenRevoke(
        user_id="tuU7smH86zAXMl76sua6xQ",
        org_id="IAsl3dl40aSsfLKiU76",
        session_id="IAsl3dl40aSsfLKiU76",
    ) # BulkTokenRevoke | Token to revoke

    # example passing only required values which don't have defaults set
    try:
        # Revoke a set of tokens
        api_response = api_instance.create_bulk_revoke_token_task(bulk_token_revoke)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_bulk_revoke_token_task: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_token_revoke** | [**BulkTokenRevoke**](BulkTokenRevoke.md)| Token to revoke |

### Return type

[**BulkTokenRevokeResponse**](BulkTokenRevokeResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | tokens have been revoked |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_introspect_token**
> Token create_introspect_token(token_introspect)

Introspect a token

Introspect a token

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.token import Token
from agilicus_api.model.token_introspect import TokenIntrospect
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    token_introspect = TokenIntrospect(
        token="token_example",
        introspect_options=TokenIntrospectOptions(
            exclude_roles=False,
            support_http_matchers=True,
            target_org_info=OrgInfo(
                target_orgs=["org-1","org-2"],
                target_domain="app1.example.com",
            ),
            no_cache=False,
        ),
    ) # TokenIntrospect | Token to introspect

    # example passing only required values which don't have defaults set
    try:
        # Introspect a token
        api_response = api_instance.create_introspect_token(token_introspect)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_introspect_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_introspect** | [**TokenIntrospect**](TokenIntrospect.md)| Token to introspect |

### Return type

[**Token**](Token.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Traffic token |  -  |
**410** | Token has been revoked |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_introspect_token_all_sub_orgs**
> ManyOrgTokenIntrospectResponse create_introspect_token_all_sub_orgs(token_introspect)

Introspect a token in all sub orgs

Introspect a token in all sub orgs

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.many_org_token_introspect_response import ManyOrgTokenIntrospectResponse
from agilicus_api.model.token_introspect import TokenIntrospect
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    token_introspect = TokenIntrospect(
        token="token_example",
        introspect_options=TokenIntrospectOptions(
            exclude_roles=False,
            support_http_matchers=True,
            target_org_info=OrgInfo(
                target_orgs=["org-1","org-2"],
                target_domain="app1.example.com",
            ),
            no_cache=False,
        ),
    ) # TokenIntrospect | Token to introspect

    # example passing only required values which don't have defaults set
    try:
        # Introspect a token in all sub orgs
        api_response = api_instance.create_introspect_token_all_sub_orgs(token_introspect)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_introspect_token_all_sub_orgs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_introspect** | [**TokenIntrospect**](TokenIntrospect.md)| Token to introspect |

### Return type

[**ManyOrgTokenIntrospectResponse**](ManyOrgTokenIntrospectResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Traffic token |  -  |
**410** | Token has been revoked |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_reissued_token**
> RawToken create_reissued_token(token_reissue_request)

Issue a new token from another

Issues a new token with the same or reduced scope to the one presented. Use this to retrieve a token for accessing a different organisation than the one you're currently operating on. Note that the presented token remains valid if it already was. If it is not valid, or the you do not have permissions in the requested organisation, the request will fail. The token will expire at the same time as the presented token. 

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.token_reissue_request import TokenReissueRequest
from agilicus_api.model.raw_token import RawToken
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    token_reissue_request = TokenReissueRequest(
        token="token_example",
        org_id="org_id_example",
    ) # TokenReissueRequest | The token request

    # example passing only required values which don't have defaults set
    try:
        # Issue a new token from another
        api_response = api_instance.create_reissued_token(token_reissue_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_reissued_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_reissue_request** | [**TokenReissueRequest**](TokenReissueRequest.md)| The token request |

### Return type

[**RawToken**](RawToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The token was succesfully issued. It is contained in the response.  |  -  |
**400** | The token reissue request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_revoke_token_task**
> create_revoke_token_task(token_revoke)

Revoke a token

Revoke a token

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.token_revoke import TokenRevoke
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    token_revoke = TokenRevoke(
        token="token_example",
        all_sessions=True,
    ) # TokenRevoke | Token to revoke

    # example passing only required values which don't have defaults set
    try:
        # Revoke a token
        api_instance.create_revoke_token_task(token_revoke)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_revoke_token_task: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_revoke** | [**TokenRevoke**](TokenRevoke.md)| Token to revoke |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | token has been revoked |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session**
> Session create_session(session)

Create a session

Create a session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.session import Session
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
    api_instance = tokens_api.TokensApi(api_client)
    session = Session(
        metadata=MetadataWithId(),
        spec=SessionsSpec(
            user_id="asdfghjklmn123",
            org_id="asdfghjklmn123",
            revoked=False,
            number_of_logins=3,
            number_of_failed_multi_factor_challenges=3,
            mfa_done=True,
        ),
        status=SessionStatus(
            challenge_id="challenge_id_example",
            last_mfa_time=1709820743,
            webpush_sent=0,
            last_webpush=dateutil_parser('1970-01-01T00:00:00.00Z'),
        ),
    ) # Session | 

    # example passing only required values which don't have defaults set
    try:
        # Create a session
        api_response = api_instance.create_session(session)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_session: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session** | [**Session**](Session.md)|  |

### Return type

[**Session**](Session.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New Session |  -  |
**400** | The token or session request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session_and_token**
> CreateSessionAndTokenRequest create_session_and_token(create_session_and_token_response)

Create a session and a token associated with the session

Create a session and a token associated with the session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.create_session_and_token_request import CreateSessionAndTokenRequest
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.create_session_and_token_response import CreateSessionAndTokenResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    create_session_and_token_response = CreateSessionAndTokenResponse(
        token=RawToken(
            token="token_example",
            refresh_token="refresh_token_example",
            time_validity=TimeValidity(
                duration=1,
            ),
            user=User(),
        ),
        session=Session(
            metadata=MetadataWithId(),
            spec=SessionsSpec(
                user_id="asdfghjklmn123",
                org_id="asdfghjklmn123",
                revoked=False,
                number_of_logins=3,
                number_of_failed_multi_factor_challenges=3,
                mfa_done=True,
            ),
            status=SessionStatus(
                challenge_id="challenge_id_example",
                last_mfa_time=1709820743,
                webpush_sent=0,
                last_webpush=dateutil_parser('1970-01-01T00:00:00.00Z'),
            ),
        ),
    ) # CreateSessionAndTokenResponse | 

    # example passing only required values which don't have defaults set
    try:
        # Create a session and a token associated with the session
        api_response = api_instance.create_session_and_token(create_session_and_token_response)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_session_and_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_session_and_token_response** | [**CreateSessionAndTokenResponse**](CreateSessionAndTokenResponse.md)|  |

### Return type

[**CreateSessionAndTokenRequest**](CreateSessionAndTokenRequest.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New Session and token created |  -  |
**400** | The token or session request is invalid |  -  |
**403** | The token or session request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session_challenge**
> SessionChallenge create_session_challenge(session_challenge)

Create a user challenge request for a session

Create a user challenge request for a session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.session_challenge import SessionChallenge
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
    api_instance = tokens_api.TokensApi(api_client)
    session_challenge = SessionChallenge(
        spec=SessionChallengeSpec(
            webpush=True,
            description="description_example",
        ),
        status=SessionChallengeStatus(
            description="description_example",
            challenge=Challenge(
                metadata=MetadataWithId(),
                spec=ChallengeSpec(
                    challenge_type="challenge_type_example",
                    challenge_types=[
                        "challenge_types_example",
                    ],
                    send_now=False,
                    timeout_seconds=600,
                    response_uri="https://auth.egov.city/mfa-answer",
                    origin="origin_example",
                    challenge_endpoints=[
                        ChallengeEndpoint(
                            endpoint="endpoint_example",
                            type="type_example",
                        ),
                    ],
                    answer_data={},
                ),
                status=ChallengeStatus(
                    state="issued",
                    public_challenge="public_challenge_example",
                    code="at4Bk6Aad39",
                    answered_at=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                ),
            ),
            session=Session(
                metadata=MetadataWithId(),
                spec=SessionsSpec(
                    user_id="asdfghjklmn123",
                    org_id="asdfghjklmn123",
                    revoked=False,
                    number_of_logins=3,
                    number_of_failed_multi_factor_challenges=3,
                    mfa_done=True,
                ),
                status=SessionStatus(
                    challenge_id="challenge_id_example",
                    last_mfa_time=1709820743,
                    webpush_sent=0,
                    last_webpush=dateutil_parser('1970-01-01T00:00:00.00Z'),
                ),
            ),
            webauthn_enrollments=[
                WebAuthNEnrollment(
                    metadata=MetadataWithId(),
                    spec=WebAuthNEnrollmentSpec(
                        user_id="123",
                        relying_party_id="123",
                        attestation_format="platform",
                        attestation_conveyance="direct",
                        user_verification="discouraged",
                        http_endpoint="https://webauthn.example.com/authenticate",
                    ),
                    status=WebAuthNEnrollmentStatus(
                        challenge="asdas43ADlaksda8739asfoafsalkasjd",
                        credential_id='YQ==',
                        transports=[
                            "ble",
                        ],
                    ),
                ),
            ],
        ),
    ) # SessionChallenge | session challenge

    # example passing only required values which don't have defaults set
    try:
        # Create a user challenge request for a session
        api_response = api_instance.create_session_challenge(session_challenge)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_session_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_challenge** | [**SessionChallenge**](SessionChallenge.md)| session challenge |

### Return type

[**SessionChallenge**](SessionChallenge.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New session challenge created |  -  |
**400** | The token or session request is invalid |  -  |
**403** | The token or session request is invalid |  -  |
**409** | The session challenge existed. Existing one returned in body. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_token**
> RawToken create_token(create_token_request)

Create a token

Create a token

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.raw_token import RawToken
from agilicus_api.model.create_token_request import CreateTokenRequest
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
    api_instance = tokens_api.TokensApi(api_client)
    create_token_request = CreateTokenRequest(
        sub="123",
        org="123",
        roles={
            "key": "key_example",
        },
        audiences=[
            "audiences_example",
        ],
        time_validity=TimeValidity(
            duration=1,
        ),
        hosts=[
            HostPermissions(
                upstream_host="upstream_host_example",
                allowed_list=[
                    RenderedRule(
                        methods=[
                            "get",
                        ],
                        paths=[
                            "paths_example",
                        ],
                        template_paths=[
                            TemplatePath(
                                template="/collection/{guid}/subcollection/{sub_guid}",
                                prefix=False,
                            ),
                        ],
                        query_parameters=[
                            RenderedQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                            ),
                        ],
                        body=RenderedRuleBody(
                            json=[
                                JSONBodyConstraint(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
                        ),
                        resource_info=ResourceInfo(
                        ),
                        matchers=RuleMatcherList(
                            matchers=[
                                RuleMatcher(
                                    extractor_name="resource_guid",
                                    inverted=False,
                                    join_operation="and",
                                    criteria=[
                                        RuleMatchCriteria(
                                            operator="equals",
                                            match_literal=None,
                                            match_extractor="port",
                                        ),
                                    ],
                                ),
                            ],
                            join_operation="and",
                        ),
                        separate_query=True,
                    ),
                ],
            ),
        ],
        token_validity=TokenValidity(
            start=dateutil_parser('1970-01-01T00:00:00.00Z'),
            duration=1,
            end=dateutil_parser('1970-01-01T00:00:00.00Z'),
            does_not_expire=False,
        ),
        session="123",
        scopes=[
            TokenScope("urn:agilicus:users:owner"),
        ],
        inherit_session=True,
        create_refresh_token=True,
        get_user=True,
    ) # CreateTokenRequest | Rule to sign

    # example passing only required values which don't have defaults set
    try:
        # Create a token
        api_response = api_instance.create_token(create_token_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_token_request** | [**CreateTokenRequest**](CreateTokenRequest.md)| Rule to sign |

### Return type

[**RawToken**](RawToken.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully signed assertion |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_token_validation**
> CreateTokenRequest create_token_validation(create_token_request)

Validate a token request

Validate a token request prior to creating a token. This verifies the user has permission to access the scopes requested

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.create_token_request import CreateTokenRequest
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)
    create_token_request = CreateTokenRequest(
        sub="123",
        org="123",
        roles={
            "key": "key_example",
        },
        audiences=[
            "audiences_example",
        ],
        time_validity=TimeValidity(
            duration=1,
        ),
        hosts=[
            HostPermissions(
                upstream_host="upstream_host_example",
                allowed_list=[
                    RenderedRule(
                        methods=[
                            "get",
                        ],
                        paths=[
                            "paths_example",
                        ],
                        template_paths=[
                            TemplatePath(
                                template="/collection/{guid}/subcollection/{sub_guid}",
                                prefix=False,
                            ),
                        ],
                        query_parameters=[
                            RenderedQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                            ),
                        ],
                        body=RenderedRuleBody(
                            json=[
                                JSONBodyConstraint(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
                        ),
                        resource_info=ResourceInfo(
                        ),
                        matchers=RuleMatcherList(
                            matchers=[
                                RuleMatcher(
                                    extractor_name="resource_guid",
                                    inverted=False,
                                    join_operation="and",
                                    criteria=[
                                        RuleMatchCriteria(
                                            operator="equals",
                                            match_literal=None,
                                            match_extractor="port",
                                        ),
                                    ],
                                ),
                            ],
                            join_operation="and",
                        ),
                        separate_query=True,
                    ),
                ],
            ),
        ],
        token_validity=TokenValidity(
            start=dateutil_parser('1970-01-01T00:00:00.00Z'),
            duration=1,
            end=dateutil_parser('1970-01-01T00:00:00.00Z'),
            does_not_expire=False,
        ),
        session="123",
        scopes=[
            TokenScope("urn:agilicus:users:owner"),
        ],
        inherit_session=True,
        create_refresh_token=True,
        get_user=True,
    ) # CreateTokenRequest | Token to validate

    # example passing only required values which don't have defaults set
    try:
        # Validate a token request
        api_response = api_instance.create_token_validation(create_token_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_token_validation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_token_request** | [**CreateTokenRequest**](CreateTokenRequest.md)| Token to validate |

### Return type

[**CreateTokenRequest**](CreateTokenRequest.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully validated token request. The user has permission to access specified scopes |  -  |
**403** | Token request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_user_data_token**
> RawToken create_user_data_token(create_user_data_token_request)

Create a User Data Token

User Data tokens allow a signed in user to create specific claims that can be shared with another party that can be cryptographically verified.  The resulting RawToken can be cryptographically verified with /v1/user_data_tokens/jwks 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.create_user_data_token_request import CreateUserDataTokenRequest
from agilicus_api.model.raw_token import RawToken
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
    api_instance = tokens_api.TokensApi(api_client)
    create_user_data_token_request = CreateUserDataTokenRequest(
        audiences=[
            "audiences_example",
        ],
        token_validity=TokenValidity(
            start=dateutil_parser('1970-01-01T00:00:00.00Z'),
            duration=1,
            end=dateutil_parser('1970-01-01T00:00:00.00Z'),
            does_not_expire=False,
        ),
        user_data={},
    ) # CreateUserDataTokenRequest | claims to sign

    # example passing only required values which don't have defaults set
    try:
        # Create a User Data Token
        api_response = api_instance.create_user_data_token(create_user_data_token_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->create_user_data_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_user_data_token_request** | [**CreateUserDataTokenRequest**](CreateUserDataTokenRequest.md)| claims to sign |

### Return type

[**RawToken**](RawToken.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully signed assertion |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_api_key**
> delete_api_key(api_key_id)

Delete an API Key

Deletes the requested API Key

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
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
    api_instance = tokens_api.TokensApi(api_client)
    api_key_id = "1234" # str | An API Key ID found in a path
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete an API Key
        api_instance.delete_api_key(api_key_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_api_key: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete an API Key
        api_instance.delete_api_key(api_key_id, user_id=user_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_api_key: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_id** | **str**| An API Key ID found in a path |
 **user_id** | **str**| Query based on user id | [optional]
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
**204** | API Key was deleted |  -  |
**404** | API Key does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_authentication_document**
> delete_authentication_document(document_id)

Delete a authentication document

Deletes the requested authentication document

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
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
    api_instance = tokens_api.TokensApi(api_client)
    document_id = "1234" # str | Authetication document path
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a authentication document
        api_instance.delete_authentication_document(document_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_authentication_document: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a authentication document
        api_instance.delete_authentication_document(document_id, user_id=user_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_authentication_document: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**| Authetication document path |
 **user_id** | **str**| Query based on user id | [optional]
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
**204** | authentication document was deleted |  -  |
**404** | authentication document does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session**
> delete_session(session_id)

Delete a session

Deletes the requested session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
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
    api_instance = tokens_api.TokensApi(api_client)
    session_id = "1234" # str | A login session identifier
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a session
        api_instance.delete_session(session_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_session: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a session
        api_instance.delete_session(session_id, user_id=user_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->delete_session: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**| A login session identifier |
 **user_id** | **str**| Query based on user id | [optional]
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
**204** | Session was deleted |  -  |
**404** | Session does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_api_key**
> APIKey get_api_key(api_key_id)

Get an API Key

Gets the requested API Key

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.api_key import APIKey
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
    api_instance = tokens_api.TokensApi(api_client)
    api_key_id = "1234" # str | An API Key ID found in a path
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an API Key
        api_response = api_instance.get_api_key(api_key_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_api_key: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an API Key
        api_response = api_instance.get_api_key(api_key_id, user_id=user_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_api_key: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_id** | **str**| An API Key ID found in a path |
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**APIKey**](APIKey.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API Key found and returned |  -  |
**404** | API Key does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_authentication_document**
> AuthenticationDocument get_authentication_document(document_id)

Get a authentication document

Gets the requested authentication document

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.authentication_document import AuthenticationDocument
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
    api_instance = tokens_api.TokensApi(api_client)
    document_id = "1234" # str | Authetication document path
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a authentication document
        api_response = api_instance.get_authentication_document(document_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_authentication_document: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a authentication document
        api_response = api_instance.get_authentication_document(document_id, user_id=user_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_authentication_document: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**| Authetication document path |
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**AuthenticationDocument**](AuthenticationDocument.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | authentication document found and returned |  -  |
**404** | authentication document does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jwks**
> ListJWKS get_jwks()

Return JSON Web Key Set (JWKS)

Return a list of JSON object that represents a cryptographic key. The members of the object represent properties of the key, including its value.

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.list_jwks import ListJWKS
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Return JSON Web Key Set (JWKS)
        api_response = api_instance.get_jwks()
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_jwks: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**ListJWKS**](ListJWKS.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return JSON Web Key Set (JWKS) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session**
> Session get_session(session_id)

Get a session

Gets the requested session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.session import Session
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
    api_instance = tokens_api.TokensApi(api_client)
    session_id = "1234" # str | A login session identifier
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a session
        api_response = api_instance.get_session(session_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_session: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a session
        api_response = api_instance.get_session(session_id, user_id=user_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_session: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**| A login session identifier |
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Session**](Session.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Session found and returned |  -  |
**404** | Session does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_token**
> Token get_token()

introspect token

\"introspect a token that is provided via the bearer authorization header\" 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.token import Token
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
    api_instance = tokens_api.TokensApi(api_client)
    exclude_roles = True # bool | Excludes complex role information from a token query (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # introspect token
        api_response = api_instance.get_token(exclude_roles=exclude_roles)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **exclude_roles** | **bool**| Excludes complex role information from a token query | [optional]

### Return type

[**Token**](Token.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Token |  -  |
**400** | token missing jti |  -  |
**404** | token not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_data_jwks**
> ListJWKS get_user_data_jwks()

Return JSON Web Key Set (JWKS)

Return a list of JSON object that represents a cryptographic key. The members of the object represent properties of the key, including its value.

### Example

```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.list_jwks import ListJWKS
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = tokens_api.TokensApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Return JSON Web Key Set (JWKS)
        api_response = api_instance.get_user_data_jwks()
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->get_user_data_jwks: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**ListJWKS**](ListJWKS.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return JSON Web Key Set (JWKS) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_keys**
> ListAPIKeysResponse list_api_keys()

List API Keys

Lists API Keys according to query parameters

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.api_key_op_status import APIKeyOpStatus
from agilicus_api.model.list_api_keys_response import ListAPIKeysResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    search_direction = "forwards" # str | Direction which the search should go starting from the email_nullable_query parameter.  (optional) if omitted the server will use the default value of "forwards"
    api_key_op_status = APIKeyOpStatus("["active"]") # APIKeyOpStatus | Filters the api keys to only those with an operational status in the provided list.  (optional)
    sort_order = "descending" # str | Whether to sort results ascending or descending. The default behaviour is ascending.  (optional) if omitted the server will use the default value of "ascending"
    page_at_created_date = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime, none_type | Pagination based query with the created date as the key. To get the initial entries supply a null value. On subsequent requests, supply the `page_at_created_date` field from the list response.  (optional)
    not_api_key_op_status = APIKeyOpStatus("["expired"]") # APIKeyOpStatus | Filters the api keys to only those without an operational status in the provided list.  (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)
    valid_at = "in 30 days" # str | Search criteria for finding api_keys that are valid (not expired) at specific time * In UTC. * Supports human-friendly values. * Example, find all valid certificates as of now:  valid_at=\"now\"  (optional)
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    scopes = ["urn:agilicus:desktop:%"] # [str] | Query a token containing scopes, case insensitive. The scope can be specific or wildcarded with '%'. This string is passed in the SQL search with ilike.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List API Keys
        api_response = api_instance.list_api_keys(limit=limit, user_id=user_id, org_id=org_id, search_direction=search_direction, api_key_op_status=api_key_op_status, sort_order=sort_order, page_at_created_date=page_at_created_date, not_api_key_op_status=not_api_key_op_status, label=label, valid_at=valid_at, name=name, scopes=scopes)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->list_api_keys: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **search_direction** | **str**| Direction which the search should go starting from the email_nullable_query parameter.  | [optional] if omitted the server will use the default value of "forwards"
 **api_key_op_status** | **APIKeyOpStatus**| Filters the api keys to only those with an operational status in the provided list.  | [optional]
 **sort_order** | **str**| Whether to sort results ascending or descending. The default behaviour is ascending.  | [optional] if omitted the server will use the default value of "ascending"
 **page_at_created_date** | **datetime, none_type**| Pagination based query with the created date as the key. To get the initial entries supply a null value. On subsequent requests, supply the &#x60;page_at_created_date&#x60; field from the list response.  | [optional]
 **not_api_key_op_status** | **APIKeyOpStatus**| Filters the api keys to only those without an operational status in the provided list.  | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]
 **valid_at** | **str**| Search criteria for finding api_keys that are valid (not expired) at specific time * In UTC. * Supports human-friendly values. * Example, find all valid certificates as of now:  valid_at&#x3D;\&quot;now\&quot;  | [optional]
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **scopes** | **[str]**| Query a token containing scopes, case insensitive. The scope can be specific or wildcarded with &#39;%&#39;. This string is passed in the SQL search with ilike.  | [optional]

### Return type

[**ListAPIKeysResponse**](ListAPIKeysResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of API Keys |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_authentication_documents**
> ListAuthenticationDocumentResponse list_authentication_documents()

List authentication documents

Lists authentication documents according to query parameters

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.list_authentication_document_response import ListAuthenticationDocumentResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List authentication documents
        api_response = api_instance.list_authentication_documents(limit=limit, user_id=user_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->list_authentication_documents: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListAuthenticationDocumentResponse**](ListAuthenticationDocumentResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of authentication documents |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_sessions**
> ListSessionsResponse list_sessions()

List Sessions

Lists Sessions according to query parameters

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.list_sessions_response import ListSessionsResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    revoked = False # bool | Query a session or token based on its revocation status (optional)
    created_time = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime | Query based on the created time. Any records created after this date will be returned. (optional)
    previous_created_time = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime | Pagination based query with the created time as the key. To get the initial entries supply an empty string. This is typically combined with another pagination key to form a composite pagination key. In that case the resulting dataset from the first key is then sub-paginated with this key. (optional)
    previous_user_id = "abc123iamanid" # str | Pagination based query with the user's id as the key. To get the initial entries supply an empty string. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List Sessions
        api_response = api_instance.list_sessions(limit=limit, user_id=user_id, org_id=org_id, revoked=revoked, created_time=created_time, previous_created_time=previous_created_time, previous_user_id=previous_user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->list_sessions: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **revoked** | **bool**| Query a session or token based on its revocation status | [optional]
 **created_time** | **datetime**| Query based on the created time. Any records created after this date will be returned. | [optional]
 **previous_created_time** | **datetime**| Pagination based query with the created time as the key. To get the initial entries supply an empty string. This is typically combined with another pagination key to form a composite pagination key. In that case the resulting dataset from the first key is then sub-paginated with this key. | [optional]
 **previous_user_id** | **str**| Pagination based query with the user&#39;s id as the key. To get the initial entries supply an empty string. | [optional]

### Return type

[**ListSessionsResponse**](ListSessionsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of sessions |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_tokens**
> ListTokensResponse list_tokens()

Query tokens

Query tokens

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.list_tokens_response import ListTokensResponse
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
    api_instance = tokens_api.TokensApi(api_client)
    limit = 100 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 100
    sub = "sub_example" # str | search criteria sub (optional)
    exp_from = "exp_from_example" # str | search criteria expired from using dateparser (optional)
    exp_to = "exp_to_example" # str | search criteria expired to using dateparser (optional)
    iat_from = "iat_from_example" # str | search criteria issued from using dateparser (optional)
    iat_to = "iat_to_example" # str | search criteria issued to using dateparser (optional)
    jti = "jti_example" # str | search criteria using jti (optional)
    org = "org_example" # str | search criteria using org (optional)
    revoked = True # bool | search criteria for revoked tokens (optional)
    session = "session_example" # str | search criteria using session (optional)
    scopes = ["urn:agilicus:desktop:%"] # [str] | Query a token containing scopes, case insensitive. The scope can be specific or wildcarded with '%'. This string is passed in the SQL search with ilike.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query tokens
        api_response = api_instance.list_tokens(limit=limit, sub=sub, exp_from=exp_from, exp_to=exp_to, iat_from=iat_from, iat_to=iat_to, jti=jti, org=org, revoked=revoked, session=session, scopes=scopes)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->list_tokens: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 100
 **sub** | **str**| search criteria sub | [optional]
 **exp_from** | **str**| search criteria expired from using dateparser | [optional]
 **exp_to** | **str**| search criteria expired to using dateparser | [optional]
 **iat_from** | **str**| search criteria issued from using dateparser | [optional]
 **iat_to** | **str**| search criteria issued to using dateparser | [optional]
 **jti** | **str**| search criteria using jti | [optional]
 **org** | **str**| search criteria using org | [optional]
 **revoked** | **bool**| search criteria for revoked tokens | [optional]
 **session** | **str**| search criteria using session | [optional]
 **scopes** | **[str]**| Query a token containing scopes, case insensitive. The scope can be specific or wildcarded with &#39;%&#39;. This string is passed in the SQL search with ilike.  | [optional]

### Return type

[**ListTokensResponse**](ListTokensResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return traffic tokens list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh_token**
> RawToken refresh_token(refresh_token_request)

Refresh a token

Refresh a token

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.refresh_token_request import RefreshTokenRequest
from agilicus_api.model.raw_token import RawToken
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
    api_instance = tokens_api.TokensApi(api_client)
    refresh_token_request = RefreshTokenRequest(
        token="token_example",
    ) # RefreshTokenRequest | RefreshTokenRequest

    # example passing only required values which don't have defaults set
    try:
        # Refresh a token
        api_response = api_instance.refresh_token(refresh_token_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->refresh_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **refresh_token_request** | [**RefreshTokenRequest**](RefreshTokenRequest.md)| RefreshTokenRequest |

### Return type

[**RawToken**](RawToken.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | token successfully refreshed |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_api_key**
> APIKey replace_api_key(api_key_id, api_key)

Update an API key

Update an API key

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.api_key import APIKey
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
    api_instance = tokens_api.TokensApi(api_client)
    api_key_id = "1234" # str | An API Key ID found in a path
    api_key = APIKey(
        metadata=MetadataWithId(),
        spec=APIKeySpec(
            user_id="123",
            org_id="123",
            expiry=dateutil_parser('2002-10-02T10:00:00-05:00'),
            session="123",
            scopes=[
                TokenScope("urn:agilicus:users:owner"),
            ],
            name="my-tool-api-key",
            label="automated-share-access",
        ),
        status=APIKeyStatus(
            api_key="api_key_example",
            token_id="123",
            creating_sub="9Xd8s0d2kd",
            creating_org="5Xd8s0d2kd",
            masquerading=False,
            oper_status=APIKeyOpStatus("active"),
        ),
    ) # APIKey | 
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update an API key
        api_response = api_instance.replace_api_key(api_key_id, api_key)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->replace_api_key: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update an API key
        api_response = api_instance.replace_api_key(api_key_id, api_key, user_id=user_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->replace_api_key: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_id** | **str**| An API Key ID found in a path |
 **api_key** | [**APIKey**](APIKey.md)|  |
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**APIKey**](APIKey.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | APIKey updated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_session**
> Session replace_session(session_id, session)

Update a session

Update a session

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.session import Session
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
    api_instance = tokens_api.TokensApi(api_client)
    session_id = "1234" # str | A login session identifier
    session = Session(
        metadata=MetadataWithId(),
        spec=SessionsSpec(
            user_id="asdfghjklmn123",
            org_id="asdfghjklmn123",
            revoked=False,
            number_of_logins=3,
            number_of_failed_multi_factor_challenges=3,
            mfa_done=True,
        ),
        status=SessionStatus(
            challenge_id="challenge_id_example",
            last_mfa_time=1709820743,
            webpush_sent=0,
            last_webpush=dateutil_parser('1970-01-01T00:00:00.00Z'),
        ),
    ) # Session | 

    # example passing only required values which don't have defaults set
    try:
        # Update a session
        api_response = api_instance.replace_session(session_id, session)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->replace_session: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**| A login session identifier |
 **session** | [**Session**](Session.md)|  |

### Return type

[**Session**](Session.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Session updated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_session_challenge**
> SessionChallenge update_session_challenge(session_challenge)

Update a session with its challenge answer

Update a session with its challenge answer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.session_challenge import SessionChallenge
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
    api_instance = tokens_api.TokensApi(api_client)
    session_challenge = SessionChallenge(
        spec=SessionChallengeSpec(
            webpush=True,
            description="description_example",
        ),
        status=SessionChallengeStatus(
            description="description_example",
            challenge=Challenge(
                metadata=MetadataWithId(),
                spec=ChallengeSpec(
                    challenge_type="challenge_type_example",
                    challenge_types=[
                        "challenge_types_example",
                    ],
                    send_now=False,
                    timeout_seconds=600,
                    response_uri="https://auth.egov.city/mfa-answer",
                    origin="origin_example",
                    challenge_endpoints=[
                        ChallengeEndpoint(
                            endpoint="endpoint_example",
                            type="type_example",
                        ),
                    ],
                    answer_data={},
                ),
                status=ChallengeStatus(
                    state="issued",
                    public_challenge="public_challenge_example",
                    code="at4Bk6Aad39",
                    answered_at=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                ),
            ),
            session=Session(
                metadata=MetadataWithId(),
                spec=SessionsSpec(
                    user_id="asdfghjklmn123",
                    org_id="asdfghjklmn123",
                    revoked=False,
                    number_of_logins=3,
                    number_of_failed_multi_factor_challenges=3,
                    mfa_done=True,
                ),
                status=SessionStatus(
                    challenge_id="challenge_id_example",
                    last_mfa_time=1709820743,
                    webpush_sent=0,
                    last_webpush=dateutil_parser('1970-01-01T00:00:00.00Z'),
                ),
            ),
            webauthn_enrollments=[
                WebAuthNEnrollment(
                    metadata=MetadataWithId(),
                    spec=WebAuthNEnrollmentSpec(
                        user_id="123",
                        relying_party_id="123",
                        attestation_format="platform",
                        attestation_conveyance="direct",
                        user_verification="discouraged",
                        http_endpoint="https://webauthn.example.com/authenticate",
                    ),
                    status=WebAuthNEnrollmentStatus(
                        challenge="asdas43ADlaksda8739asfoafsalkasjd",
                        credential_id='YQ==',
                        transports=[
                            "ble",
                        ],
                    ),
                ),
            ],
        ),
    ) # SessionChallenge | session challenge

    # example passing only required values which don't have defaults set
    try:
        # Update a session with its challenge answer
        api_response = api_instance.update_session_challenge(session_challenge)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->update_session_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_challenge** | [**SessionChallenge**](SessionChallenge.md)| session challenge |

### Return type

[**SessionChallenge**](SessionChallenge.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Session challenge found |  -  |
**404** | Session challenge does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_identity_assertion**
> IdentityAssertionResponse validate_identity_assertion(identity_assertion)

Validate an identity assertion

Validate an identity assertion to asscertain if the request for a token is valid

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import tokens_api
from agilicus_api.model.identity_assertion_response import IdentityAssertionResponse
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.identity_assertion import IdentityAssertion
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
    api_instance = tokens_api.TokensApi(api_client)
    identity_assertion = IdentityAssertion(
        authentication_document_id="asdfghjklmn123",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    ) # IdentityAssertion | Token to validate

    # example passing only required values which don't have defaults set
    try:
        # Validate an identity assertion
        api_response = api_instance.validate_identity_assertion(identity_assertion)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling TokensApi->validate_identity_assertion: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **identity_assertion** | [**IdentityAssertion**](IdentityAssertion.md)| Token to validate |

### Return type

[**IdentityAssertionResponse**](IdentityAssertionResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully validated the identity assertion |  -  |
**400** | The identity assertion is invalid. This can be for a number of reasons. Including an invalid identifier, invalid signature, or invalid contents. The error_code property can provide some information on why the failure occured. In particular, the following codes:  - &#x60;USER_UNKNOWN&#x60;: The identity asserted was for a non-existant user.  - &#x60;AUTHENTICATION_DOCUMENT_UKNOWN&#x60;: The authentication document did not exist.  - &#x60;AUTHENTICATION_DOCUMENT_EXPIRED&#x60;: The authentication document has expired.  - &#x60;IDENTITY_ASSERTION_INVALID&#x60;: The identity assertion failed validation (signature, user id, etc).  - &#x60;IDENTITY_ASSERTION_EXPIRED&#x60;: The identity assertion has expired -- it was created too far in the past.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

