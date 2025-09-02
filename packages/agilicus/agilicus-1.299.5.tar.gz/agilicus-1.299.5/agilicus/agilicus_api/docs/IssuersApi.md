# agilicus_api.IssuersApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_client**](IssuersApi.md#create_client) | **POST** /v1/clients | Create a client
[**create_issuer**](IssuersApi.md#create_issuer) | **POST** /v1/issuers/issuer_roots | Create an issuer
[**create_policy**](IssuersApi.md#create_policy) | **POST** /v1/issuers/authentication_policies | Create a policy
[**create_policy_rule**](IssuersApi.md#create_policy_rule) | **POST** /v1/issuers/authentication_policies/{policy_id}/policy_rules | Create a policy rule
[**create_upstream_alias**](IssuersApi.md#create_upstream_alias) | **POST** /v1/issuers/issuer_extensions/{issuer_id}/upstream_aliases | Create an upstream alias
[**create_upstream_group_mapping**](IssuersApi.md#create_upstream_group_mapping) | **POST** /v1/issuers/issuer_extensions/{issuer_id}/upstream_group_mapping | Create an upstream group mapping
[**delete_client**](IssuersApi.md#delete_client) | **DELETE** /v1/clients/{client_id} | Delete a client
[**delete_policy**](IssuersApi.md#delete_policy) | **DELETE** /v1/issuers/authentication_policies/{policy_id} | Delete a Policy
[**delete_policy_rule**](IssuersApi.md#delete_policy_rule) | **DELETE** /v1/issuers/authentication_policies/{policy_id}/policy_rules/{policy_rule_id} | Delete a Policy Rule
[**delete_root**](IssuersApi.md#delete_root) | **DELETE** /v1/issuers/issuer_roots/{issuer_id} | Delete an Issuer
[**delete_upstream_alias**](IssuersApi.md#delete_upstream_alias) | **DELETE** /v1/issuers/issuer_extensions/{issuer_id}/upstream_aliases/{upstream_alias_id} | Delete an upstream alias
[**delete_upstream_group_mapping**](IssuersApi.md#delete_upstream_group_mapping) | **DELETE** /v1/issuers/issuer_extensions/{issuer_id}/upstream_group_mapping/{upstream_group_mapping_id} | Delete an upstream group mapping
[**get_client**](IssuersApi.md#get_client) | **GET** /v1/clients/{client_id} | Get a client
[**get_issuer**](IssuersApi.md#get_issuer) | **GET** /v1/issuers/issuer_extensions/{issuer_id} | Get an issuer
[**get_policy**](IssuersApi.md#get_policy) | **GET** /v1/issuers/authentication_policies/{policy_id} | Get a policy
[**get_policy_rule**](IssuersApi.md#get_policy_rule) | **GET** /v1/issuers/authentication_policies/{policy_id}/policy_rules/{policy_rule_id} | Get a policy rule
[**get_root**](IssuersApi.md#get_root) | **GET** /v1/issuers/issuer_roots/{issuer_id} | Get an issuer
[**get_upstream_alias**](IssuersApi.md#get_upstream_alias) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/upstream_aliases/{upstream_alias_id} | Get an upstream alias
[**get_upstream_group_mapping**](IssuersApi.md#get_upstream_group_mapping) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/upstream_group_mapping/{upstream_group_mapping_id} | Get an upstream group mapping
[**get_upstreams**](IssuersApi.md#get_upstreams) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/upstreams | Get provisioned upstreams for the issuer
[**get_wellknown_issuer_info**](IssuersApi.md#get_wellknown_issuer_info) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/well_known_info | Get well-known issuer information
[**list_clients**](IssuersApi.md#list_clients) | **GET** /v1/clients | Query Clients
[**list_issuer_roots**](IssuersApi.md#list_issuer_roots) | **GET** /v1/issuers/issuer_roots | Query Issuers
[**list_issuer_upstreams**](IssuersApi.md#list_issuer_upstreams) | **GET** /v1/issuer_upstreams | list issuer upstream information
[**list_issuers**](IssuersApi.md#list_issuers) | **GET** /v1/issuers/issuer_extensions | Query Issuers
[**list_policies**](IssuersApi.md#list_policies) | **GET** /v1/issuers/authentication_policies | Query Policies
[**list_policy_rules**](IssuersApi.md#list_policy_rules) | **GET** /v1/issuers/authentication_policies/{policy_id}/policy_rules | Query Policy rules
[**list_upstream_aliases**](IssuersApi.md#list_upstream_aliases) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/upstream_aliases | Query upstream aliases for an issuer
[**list_upstream_group_mappings**](IssuersApi.md#list_upstream_group_mappings) | **GET** /v1/issuers/issuer_extensions/{issuer_id}/upstream_group_mapping | Query upstream group mappings for an issuer
[**list_wellknown_issuer_info**](IssuersApi.md#list_wellknown_issuer_info) | **GET** /v1/issuers/issuer_extensions/well_known_info | list well-known issuer information
[**replace_client**](IssuersApi.md#replace_client) | **PUT** /v1/clients/{client_id} | Update a client
[**replace_issuer**](IssuersApi.md#replace_issuer) | **PUT** /v1/issuers/issuer_extensions/{issuer_id} | Update an issuer
[**replace_policy**](IssuersApi.md#replace_policy) | **PUT** /v1/issuers/authentication_policies/{policy_id} | Update a policy
[**replace_policy_rule**](IssuersApi.md#replace_policy_rule) | **PUT** /v1/issuers/authentication_policies/{policy_id}/policy_rules/{policy_rule_id} | Update a policy rule
[**replace_root**](IssuersApi.md#replace_root) | **PUT** /v1/issuers/issuer_roots/{issuer_id} | Update an issuer
[**replace_upstream_alias**](IssuersApi.md#replace_upstream_alias) | **PUT** /v1/issuers/issuer_extensions/{issuer_id}/upstream_aliases/{upstream_alias_id} | Update an upstream alias
[**replace_upstream_group_mapping**](IssuersApi.md#replace_upstream_group_mapping) | **PUT** /v1/issuers/issuer_extensions/{issuer_id}/upstream_group_mapping/{upstream_group_mapping_id} | Update an upstream group mapping
[**reset_service_account**](IssuersApi.md#reset_service_account) | **POST** /v1/issuers/reset_service_account | Reset the service account for the specified issuer
[**reset_to_default_policy**](IssuersApi.md#reset_to_default_policy) | **POST** /v1/issuers/issuer_extensions/{issuer_id}/set_auth_policy_to_default | Reset the current policy to the default policy
[**set_policy**](IssuersApi.md#set_policy) | **POST** /v1/issuers/issuer_extensions/{issuer_id}/set_auth_policy | Set the current policy to the policy sent
[**validate_upstream**](IssuersApi.md#validate_upstream) | **GET** /v1/issuers/validate_upstream | Validate upstream issuer


# **create_client**
> IssuerClient create_client(issuer_client)

Create a client

Create a client

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer_client import IssuerClient
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_client = IssuerClient(
        name="name_example",
        secret="secret_example",
        application="application_example",
        org_id="org_id_example",
        restricted_organisations=["org-1","org-2"],
        saml_metadata_file="saml_metadata_file_example",
        id_mapping=["federated_claims.user_id"],
        saml_scopes=["openid","profile","email","urn:agilicus:api:users:self","federated:id"],
        organisation_scope="here_only",
        redirects=[
            "redirects_example",
        ],
        mfa_challenge="user_preference",
        single_sign_on="never",
        attributes=[
            AuthenticationAttribute(
                attribute_name="emailAddress",
                internal_attribute_path="user.email",
            ),
        ],
    ) # IssuerClient | IssuerClient

    # example passing only required values which don't have defaults set
    try:
        # Create a client
        api_response = api_instance.create_client(issuer_client)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_client: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_client** | [**IssuerClient**](IssuerClient.md)| IssuerClient |

### Return type

[**IssuerClient**](IssuerClient.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created client |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_issuer**
> Issuer create_issuer(issuer)

Create an issuer

Create an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer import Issuer
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer = Issuer(
        issuer="issuer_example",
        enabled=True,
        org_id="org_id_example",
        theme_file_id="ASsdq23lsaSSf",
        upstream_redirect_uri="upstream_redirect_uri_example",
        managed_upstreams=[
            ManagedUpstreamIdentityProvider(
                enabled=False,
                prompt_select_account=False,
            ),
        ],
        oidc_upstreams=[
            OIDCUpstreamIdentityProvider(
                name="name_example",
                icon="city-login",
                issuer="issuer_example",
                client_id="client_id_example",
                client_secret="client_secret_example",
                issuer_external_host="issuer_external_host_example",
                username_key="username_key_example",
                email_key="email_key_example",
                email_verification_required=True,
                request_user_info=True,
                user_id_key="user_id_key_example",
                auto_create_status=AutoCreateStatus("active"),
                prompt_mode="auto",
                oidc_flavor="oidc",
                client_authorization_type="federated-credential",
                admin_status=AdminStatus("active"),
                trap_disabled=True,
                operational_status=OperationalStatus(
                    status="good",
                    status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                    generation=1,
                    generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                ),
            ),
        ],
        local_auth_upstreams=[
            LocalAuthUpstreamIdentityProvider(),
        ],
        application_upstreams=[
            ApplicationUpstreamIdentityProvider(),
        ],
        kerberos_upstreams=[
            KerberosUpstreamIdentityProvider(),
        ],
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        saml_state_encryption_key="saml_state_encryption_key_example",
        admin_status=AdminStatus("active"),
        trap_disabled=True,
        operational_status=OperationalStatus(
            status="good",
            status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            generation=1,
            generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
        ),
        parent_issuer="123",
        status=IssuerStatus(
            theme_file_id="ASsdq23lsaSSf",
            operational_status=OperationalStatus(
                status="good",
                status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                generation=1,
                generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            ),
            trusted_issuers=[
                TrustedIssuer(
                    issuer="issuer_example",
                    purpose="support_request",
                ),
            ],
        ),
    ) # Issuer | Issuer

    # example passing only required values which don't have defaults set
    try:
        # Create an issuer
        api_response = api_instance.create_issuer(issuer)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_issuer: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer** | [**Issuer**](Issuer.md)| Issuer |

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created issuer |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_policy**
> Policy create_policy(policy)

Create a policy

Create a policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy import Policy
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy = Policy(
        metadata=MetadataWithId(),
        spec=PolicySpec(
            name="Staging org authentication policy",
            issuer_id="asdfg123hjkl",
            org_id="asdfg123hjkl",
            supported_mfa_methods=["totp","webauthn"],
            default_action="allow_login",
            policy_groups=[
                PolicyGroup(
                    metadata=MetadataWithId(),
                    spec=PolicyGroupSpec(
                        name="name_example",
                        rule_ids=[
                            "123",
                        ],
                    ),
                ),
            ],
            source="Default:1.0.0",
        ),
        status=PolicyStatus(
            associated_issuers=[
                PolicyIssuerRef(
                    issuer_id="123",
                    org_id="123",
                ),
            ],
        ),
    ) # Policy | Policy

    # example passing only required values which don't have defaults set
    try:
        # Create a policy
        api_response = api_instance.create_policy(policy)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy** | [**Policy**](Policy.md)| Policy |

### Return type

[**Policy**](Policy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created a Policy |  -  |
**400** | The request was invalid. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_policy_rule**
> PolicyRule create_policy_rule(policy_id, policy_rule)

Create a policy rule

Create a policy rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.policy_rule import PolicyRule
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    policy_rule = PolicyRule(
        metadata=MetadataWithId(),
        spec=PolicyRuleSpec(
            name="blocked IPs rule",
            action="enroll",
            priority=1,
            org_id="asdfg123hjkl",
            conditions=[
                PolicyCondition(
                    condition_type="type_client_id_list",
                    inverted=False,
                    input_is_list=False,
                    value="my-city-org",
                    operator="equals",
                    field="clients.name",
                ),
            ],
        ),
    ) # PolicyRule | Policy rule

    # example passing only required values which don't have defaults set
    try:
        # Create a policy rule
        api_response = api_instance.create_policy_rule(policy_id, policy_rule)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_policy_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **policy_rule** | [**PolicyRule**](PolicyRule.md)| Policy rule |

### Return type

[**PolicyRule**](PolicyRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created a Policy |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_upstream_alias**
> UpstreamAlias create_upstream_alias(issuer_id, upstream_alias)

Create an upstream alias

Create an upstream alias

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_alias import UpstreamAlias
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_alias = UpstreamAlias(
        metadata=MetadataWithId(),
        spec=UpstreamAliasSpec(
            org_id="org_id_example",
            client_id="client_id_example",
            aliases=[
                UpstreamAliasMapping(
                    upstream_provider_name="upstream_provider_name_example",
                    aliased_upstream_provider_names=[
                        "aliased_upstream_provider_names_example",
                    ],
                ),
            ],
        ),
    ) # UpstreamAlias | Upstream alias

    # example passing only required values which don't have defaults set
    try:
        # Create an upstream alias
        api_response = api_instance.create_upstream_alias(issuer_id, upstream_alias)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_upstream_alias: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_alias** | [**UpstreamAlias**](UpstreamAlias.md)| Upstream alias |

### Return type

[**UpstreamAlias**](UpstreamAlias.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created upstream alias |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_upstream_group_mapping**
> UpstreamGroupMapping create_upstream_group_mapping(issuer_id, upstream_group_mapping)

Create an upstream group mapping

Create an upstream group mapping

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_group_mapping import UpstreamGroupMapping
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_group_mapping = UpstreamGroupMapping(
        metadata=MetadataWithId(),
        spec=UpstreamGroupMappingSpec(
            upstream_issuer="https://login.microsoftonline.com/c945d377-ea94-4a7d-9c83-0615e7ff0022/v2.0",
            org_id="asdfg123hjkl",
            group_mappings=[
                UpstreamGroupMappingEntry(
                    priority=1,
                    upstream_group_name="Company Team (.*)",
                    upstream_name_is_a_guid=False,
                    agilicus_group_name="Agilicus {0}",
                    group_org_id="asdfg123hjkl",
                ),
            ],
            excluded_groups=[
                UpstreamGroupExcludedEntry(
                    upstream_group_name="Admin*",
                    upstream_name_is_a_guid=False,
                ),
            ],
        ),
    ) # UpstreamGroupMapping | Upstream Group Mapping

    # example passing only required values which don't have defaults set
    try:
        # Create an upstream group mapping
        api_response = api_instance.create_upstream_group_mapping(issuer_id, upstream_group_mapping)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->create_upstream_group_mapping: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_group_mapping** | [**UpstreamGroupMapping**](UpstreamGroupMapping.md)| Upstream Group Mapping |

### Return type

[**UpstreamGroupMapping**](UpstreamGroupMapping.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created Upstream Group Mapping |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_client**
> delete_client(client_id)

Delete a client

Delete a client

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    client_id = "1234" # str | client_id path
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a client
        api_instance.delete_client(client_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_client: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a client
        api_instance.delete_client(client_id, summarize_collection=summarize_collection, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_client: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| client_id path |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
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
**204** | Client was deleted |  -  |
**404** | Issuer/Client does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_policy**
> delete_policy(policy_id)

Delete a Policy

Delete a Policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a Policy
        api_instance.delete_policy(policy_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a Policy
        api_instance.delete_policy(policy_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
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
**204** | Policy was deleted |  -  |
**404** | Policy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_policy_rule**
> delete_policy_rule(policy_id, policy_rule_id)

Delete a Policy Rule

Delete a Policy Rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    policy_rule_id = "1234" # str | Policy Rule Unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a Policy Rule
        api_instance.delete_policy_rule(policy_id, policy_rule_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_policy_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a Policy Rule
        api_instance.delete_policy_rule(policy_id, policy_rule_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_policy_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **policy_rule_id** | **str**| Policy Rule Unique identifier |
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
**204** | Policy Rule was deleted |  -  |
**404** | Policy Rule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_root**
> delete_root(issuer_id)

Delete an Issuer

Delete an Issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete an Issuer
        api_instance.delete_root(issuer_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_root: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete an Issuer
        api_instance.delete_root(issuer_id, summarize_collection=summarize_collection, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_root: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
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
**204** | Issuer was deleted |  -  |
**404** | Issuer does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_upstream_alias**
> delete_upstream_alias(issuer_id, upstream_alias_id)

Delete an upstream alias

Delete an upstream alias

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_alias_id = "1234" # str | upstream alias id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete an upstream alias
        api_instance.delete_upstream_alias(issuer_id, upstream_alias_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_upstream_alias: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete an upstream alias
        api_instance.delete_upstream_alias(issuer_id, upstream_alias_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_upstream_alias: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_alias_id** | **str**| upstream alias id |
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
**204** | Upstream alias was deleted |  -  |
**404** | Issuer/Mapping does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_upstream_group_mapping**
> delete_upstream_group_mapping(issuer_id, upstream_group_mapping_id)

Delete an upstream group mapping

Delete an upstream group mapping

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_group_mapping_id = "1234" # str | upstream group_mapping id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete an upstream group mapping
        api_instance.delete_upstream_group_mapping(issuer_id, upstream_group_mapping_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_upstream_group_mapping: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete an upstream group mapping
        api_instance.delete_upstream_group_mapping(issuer_id, upstream_group_mapping_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->delete_upstream_group_mapping: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_group_mapping_id** | **str**| upstream group_mapping id |
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
**204** | Upstream group mapping was deleted |  -  |
**404** | Issuer/Mapping does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_client**
> IssuerClient get_client(client_id)

Get a client

Get a client

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.issuer_client import IssuerClient
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
    api_instance = issuers_api.IssuersApi(api_client)
    client_id = "1234" # str | client_id path
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a client
        api_response = api_instance.get_client(client_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_client: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a client
        api_response = api_instance.get_client(client_id, summarize_collection=summarize_collection, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_client: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| client_id path |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**IssuerClient**](IssuerClient.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return client by id |  -  |
**404** | Client not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_issuer**
> Issuer get_issuer(issuer_id)

Get an issuer

Get an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer import Issuer
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an issuer
        api_response = api_instance.get_issuer(issuer_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_issuer: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an issuer
        api_response = api_instance.get_issuer(issuer_id, summarize_collection=summarize_collection, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_issuer: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return issuer by id |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_policy**
> Policy get_policy(policy_id)

Get a policy

Get a policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.policy import Policy
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a policy
        api_response = api_instance.get_policy(policy_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a policy
        api_response = api_instance.get_policy(policy_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Policy**](Policy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return policy by id |  -  |
**404** | Policy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_policy_rule**
> PolicyRule get_policy_rule(policy_id, policy_rule_id)

Get a policy rule

Get a policy rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.policy_rule import PolicyRule
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    policy_rule_id = "1234" # str | Policy Rule Unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a policy rule
        api_response = api_instance.get_policy_rule(policy_id, policy_rule_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_policy_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a policy rule
        api_response = api_instance.get_policy_rule(policy_id, policy_rule_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_policy_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **policy_rule_id** | **str**| Policy Rule Unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**PolicyRule**](PolicyRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return policy rule by id |  -  |
**404** | Policy Rule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_root**
> Issuer get_root(issuer_id)

Get an issuer

Get an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer import Issuer
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an issuer
        api_response = api_instance.get_root(issuer_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_root: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an issuer
        api_response = api_instance.get_root(issuer_id, summarize_collection=summarize_collection, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_root: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return issuer by id |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_upstream_alias**
> UpstreamAlias get_upstream_alias(issuer_id, upstream_alias_id)

Get an upstream alias

Get an upstream alias

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_alias import UpstreamAlias
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_alias_id = "1234" # str | upstream alias id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an upstream alias
        api_response = api_instance.get_upstream_alias(issuer_id, upstream_alias_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstream_alias: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an upstream alias
        api_response = api_instance.get_upstream_alias(issuer_id, upstream_alias_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstream_alias: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_alias_id** | **str**| upstream alias id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**UpstreamAlias**](UpstreamAlias.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return upstream alias by id |  -  |
**404** | Mapping not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_upstream_group_mapping**
> UpstreamGroupMapping get_upstream_group_mapping(issuer_id, upstream_group_mapping_id)

Get an upstream group mapping

Get an upstream group mapping

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_group_mapping import UpstreamGroupMapping
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_group_mapping_id = "1234" # str | upstream group_mapping id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get an upstream group mapping
        api_response = api_instance.get_upstream_group_mapping(issuer_id, upstream_group_mapping_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstream_group_mapping: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an upstream group mapping
        api_response = api_instance.get_upstream_group_mapping(issuer_id, upstream_group_mapping_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstream_group_mapping: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_group_mapping_id** | **str**| upstream group_mapping id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**UpstreamGroupMapping**](UpstreamGroupMapping.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return upstream group mapping by id |  -  |
**404** | Mapping not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_upstreams**
> BaseUpstreams get_upstreams(issuer_id, org_id)

Get provisioned upstreams for the issuer

Get provisioned upstreams for the issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.base_upstreams import BaseUpstreams
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    org_id = "1234" # str | Organisation Unique identifier
    upstream_type = "oidc" # str | The type of issuer upstream to query on (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get provisioned upstreams for the issuer
        api_response = api_instance.get_upstreams(issuer_id, org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstreams: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get provisioned upstreams for the issuer
        api_response = api_instance.get_upstreams(issuer_id, org_id, upstream_type=upstream_type)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_upstreams: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **org_id** | **str**| Organisation Unique identifier |
 **upstream_type** | **str**| The type of issuer upstream to query on | [optional]

### Return type

[**BaseUpstreams**](BaseUpstreams.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the issuer&#39;s provisioned upstreams |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_wellknown_issuer_info**
> WellKnownIssuerInfo get_wellknown_issuer_info(issuer_id)

Get well-known issuer information

Get well-known issuer information

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.well_known_issuer_info import WellKnownIssuerInfo
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path

    # example passing only required values which don't have defaults set
    try:
        # Get well-known issuer information
        api_response = api_instance.get_wellknown_issuer_info(issuer_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->get_wellknown_issuer_info: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |

### Return type

[**WellKnownIssuerInfo**](WellKnownIssuerInfo.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the issuer&#39;s well-known information |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_clients**
> ListIssuerClientsResponse list_clients()

Query Clients

Query Clients

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_issuer_clients_response import ListIssuerClientsResponse
from agilicus_api.model.admin_status import AdminStatus
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
    api_instance = issuers_api.IssuersApi(api_client)
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    admin_status = AdminStatus("agent") # AdminStatus | admin status query (optional)
    show_deleted = True # bool | Allows overriding certain queries in the system to show deleted objects. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Clients
        api_response = api_instance.list_clients(summarize_collection=summarize_collection, limit=limit, org_id=org_id, admin_status=admin_status, show_deleted=show_deleted)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_clients: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **admin_status** | **AdminStatus**| admin status query | [optional]
 **show_deleted** | **bool**| Allows overriding certain queries in the system to show deleted objects. | [optional]

### Return type

[**ListIssuerClientsResponse**](ListIssuerClientsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return clients list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_issuer_roots**
> ListIssuerRootsResponse list_issuer_roots()

Query Issuers

Query Issuers

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_issuer_roots_response import ListIssuerRootsResponse
from agilicus_api.model.admin_status import AdminStatus
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
    api_instance = issuers_api.IssuersApi(api_client)
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    issuer = "example.com" # str | Organisation issuer (optional)
    admin_status = AdminStatus("agent") # AdminStatus | admin status query (optional)
    show_deleted = True # bool | Allows overriding certain queries in the system to show deleted objects. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Issuers
        api_response = api_instance.list_issuer_roots(summarize_collection=summarize_collection, limit=limit, issuer=issuer, admin_status=admin_status, show_deleted=show_deleted)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_issuer_roots: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **issuer** | **str**| Organisation issuer | [optional]
 **admin_status** | **AdminStatus**| admin status query | [optional]
 **show_deleted** | **bool**| Allows overriding certain queries in the system to show deleted objects. | [optional]

### Return type

[**ListIssuerRootsResponse**](ListIssuerRootsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return issuers list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_issuer_upstreams**
> ListIssuerUpstreams list_issuer_upstreams()

list issuer upstream information

list issuer upstream information

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_issuer_upstreams import ListIssuerUpstreams
from agilicus_api.model.admin_status import AdminStatus
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
    api_instance = issuers_api.IssuersApi(api_client)
    upstream_type = "oidc" # str | The type of issuer upstream to query on (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    admin_status = AdminStatus("agent") # AdminStatus | admin status query (optional)
    show_deleted = True # bool | Allows overriding certain queries in the system to show deleted objects. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list issuer upstream information
        api_response = api_instance.list_issuer_upstreams(upstream_type=upstream_type, org_id=org_id, limit=limit, admin_status=admin_status, show_deleted=show_deleted)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_issuer_upstreams: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upstream_type** | **str**| The type of issuer upstream to query on | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **admin_status** | **AdminStatus**| admin status query | [optional]
 **show_deleted** | **bool**| Allows overriding certain queries in the system to show deleted objects. | [optional]

### Return type

[**ListIssuerUpstreams**](ListIssuerUpstreams.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the list of issuer upstream information |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_issuers**
> ListIssuerExtensionsResponse list_issuers()

Query Issuers

Query Issuers

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_issuer_extensions_response import ListIssuerExtensionsResponse
from agilicus_api.model.admin_status import AdminStatus
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
    api_instance = issuers_api.IssuersApi(api_client)
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    issuer = "example.com" # str | Organisation issuer (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    admin_status = AdminStatus("agent") # AdminStatus | admin status query (optional)
    show_deleted = True # bool | Allows overriding certain queries in the system to show deleted objects. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Issuers
        api_response = api_instance.list_issuers(summarize_collection=summarize_collection, limit=limit, issuer=issuer, org_id=org_id, admin_status=admin_status, show_deleted=show_deleted)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_issuers: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **issuer** | **str**| Organisation issuer | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **admin_status** | **AdminStatus**| admin status query | [optional]
 **show_deleted** | **bool**| Allows overriding certain queries in the system to show deleted objects. | [optional]

### Return type

[**ListIssuerExtensionsResponse**](ListIssuerExtensionsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return issuers list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_policies**
> ListPoliciesResponse list_policies()

Query Policies

Query Policies

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_policies_response import ListPoliciesResponse
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
    api_instance = issuers_api.IssuersApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    issuer_id = "abc32j3ijfn" # str | Organisation issuer id (optional)
    policy_name = "MyStrongPolicy" # str | Query the policies by name (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Policies
        api_response = api_instance.list_policies(limit=limit, org_id=org_id, issuer_id=issuer_id, policy_name=policy_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_policies: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **issuer_id** | **str**| Organisation issuer id | [optional]
 **policy_name** | **str**| Query the policies by name | [optional]

### Return type

[**ListPoliciesResponse**](ListPoliciesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the list of policies |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_policy_rules**
> ListPolicyRulesResponse list_policy_rules(policy_id)

Query Policy rules

Query Policy rules

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_policy_rules_response import ListPolicyRulesResponse
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Query Policy rules
        api_response = api_instance.list_policy_rules(policy_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_policy_rules: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Policy rules
        api_response = api_instance.list_policy_rules(policy_id, limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_policy_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListPolicyRulesResponse**](ListPolicyRulesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the list of policy rules |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_upstream_aliases**
> ListUpstreamAliases list_upstream_aliases(issuer_id)

Query upstream aliases for an issuer

Query upstream aliases for an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_upstream_aliases import ListUpstreamAliases
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Query upstream aliases for an issuer
        api_response = api_instance.list_upstream_aliases(issuer_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_upstream_aliases: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query upstream aliases for an issuer
        api_response = api_instance.list_upstream_aliases(issuer_id, limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_upstream_aliases: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListUpstreamAliases**](ListUpstreamAliases.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return upstream alias list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_upstream_group_mappings**
> ListUpstreamGroupMapping list_upstream_group_mappings(issuer_id)

Query upstream group mappings for an issuer

Query upstream group mappings for an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_upstream_group_mapping import ListUpstreamGroupMapping
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Query upstream group mappings for an issuer
        api_response = api_instance.list_upstream_group_mappings(issuer_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_upstream_group_mappings: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query upstream group mappings for an issuer
        api_response = api_instance.list_upstream_group_mappings(issuer_id, limit=limit, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_upstream_group_mappings: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListUpstreamGroupMapping**](ListUpstreamGroupMapping.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return upstream group mapping list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_wellknown_issuer_info**
> ListWellKnownIssuerInfo list_wellknown_issuer_info()

list well-known issuer information

list well-known issuer information

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.list_well_known_issuer_info import ListWellKnownIssuerInfo
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
    api_instance = issuers_api.IssuersApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    issuer_id = "abc32j3ijfn" # str | Organisation issuer id (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list well-known issuer information
        api_response = api_instance.list_wellknown_issuer_info(org_id=org_id, issuer_id=issuer_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->list_wellknown_issuer_info: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **issuer_id** | **str**| Organisation issuer id | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListWellKnownIssuerInfo**](ListWellKnownIssuerInfo.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the list of well-known issuer information |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_client**
> IssuerClient replace_client(client_id, issuer_client)

Update a client

Update a client

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.issuer_client import IssuerClient
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
    api_instance = issuers_api.IssuersApi(api_client)
    client_id = "1234" # str | client_id path
    issuer_client = IssuerClient(
        name="name_example",
        secret="secret_example",
        application="application_example",
        org_id="org_id_example",
        restricted_organisations=["org-1","org-2"],
        saml_metadata_file="saml_metadata_file_example",
        id_mapping=["federated_claims.user_id"],
        saml_scopes=["openid","profile","email","urn:agilicus:api:users:self","federated:id"],
        organisation_scope="here_only",
        redirects=[
            "redirects_example",
        ],
        mfa_challenge="user_preference",
        single_sign_on="never",
        attributes=[
            AuthenticationAttribute(
                attribute_name="emailAddress",
                internal_attribute_path="user.email",
            ),
        ],
    ) # IssuerClient | Issuer client
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True

    # example passing only required values which don't have defaults set
    try:
        # Update a client
        api_response = api_instance.replace_client(client_id, issuer_client)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_client: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a client
        api_response = api_instance.replace_client(client_id, issuer_client, summarize_collection=summarize_collection)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_client: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| client_id path |
 **issuer_client** | [**IssuerClient**](IssuerClient.md)| Issuer client |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True

### Return type

[**IssuerClient**](IssuerClient.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Client was updated |  -  |
**400** | The request was invalid. Likely a field was missing or incorrectly formatted. |  -  |
**404** | Issuer/Client does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_issuer**
> Issuer replace_issuer(issuer_id, issuer)

Update an issuer

Update an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.issuer import Issuer
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    issuer = Issuer(
        issuer="issuer_example",
        enabled=True,
        org_id="org_id_example",
        theme_file_id="ASsdq23lsaSSf",
        upstream_redirect_uri="upstream_redirect_uri_example",
        managed_upstreams=[
            ManagedUpstreamIdentityProvider(
                enabled=False,
                prompt_select_account=False,
            ),
        ],
        oidc_upstreams=[
            OIDCUpstreamIdentityProvider(
                name="name_example",
                icon="city-login",
                issuer="issuer_example",
                client_id="client_id_example",
                client_secret="client_secret_example",
                issuer_external_host="issuer_external_host_example",
                username_key="username_key_example",
                email_key="email_key_example",
                email_verification_required=True,
                request_user_info=True,
                user_id_key="user_id_key_example",
                auto_create_status=AutoCreateStatus("active"),
                prompt_mode="auto",
                oidc_flavor="oidc",
                client_authorization_type="federated-credential",
                admin_status=AdminStatus("active"),
                trap_disabled=True,
                operational_status=OperationalStatus(
                    status="good",
                    status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                    generation=1,
                    generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                ),
            ),
        ],
        local_auth_upstreams=[
            LocalAuthUpstreamIdentityProvider(),
        ],
        application_upstreams=[
            ApplicationUpstreamIdentityProvider(),
        ],
        kerberos_upstreams=[
            KerberosUpstreamIdentityProvider(),
        ],
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        saml_state_encryption_key="saml_state_encryption_key_example",
        admin_status=AdminStatus("active"),
        trap_disabled=True,
        operational_status=OperationalStatus(
            status="good",
            status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            generation=1,
            generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
        ),
        parent_issuer="123",
        status=IssuerStatus(
            theme_file_id="ASsdq23lsaSSf",
            operational_status=OperationalStatus(
                status="good",
                status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                generation=1,
                generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            ),
            trusted_issuers=[
                TrustedIssuer(
                    issuer="issuer_example",
                    purpose="support_request",
                ),
            ],
        ),
    ) # Issuer | Issuer
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    force_reconcile_theme = False # bool | Forces reconciling the theme file, even if no change was made (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update an issuer
        api_response = api_instance.replace_issuer(issuer_id, issuer)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_issuer: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update an issuer
        api_response = api_instance.replace_issuer(issuer_id, issuer, summarize_collection=summarize_collection, force_reconcile_theme=force_reconcile_theme)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_issuer: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **issuer** | [**Issuer**](Issuer.md)| Issuer |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **force_reconcile_theme** | **bool**| Forces reconciling the theme file, even if no change was made | [optional]

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Issuer was updated |  -  |
**400** | The request did not match its schema, or it tried to do something that was not allowed. In particular, you cannot remove an upstream issuer when users in the organisation still log in using that issuer. In that case, an &#x60;error_code&#x60; of &#x60;UPSTREAM_IDP_STILL_HAS_USERS&#x60; will be returned. Further, if the system encountered an error retrieving the users for the upstream issuer, &#x60;UPSTREAM_IDP_FAILED_USERS_FETCH&#x60; will be returned.  |  -  |
**404** | Issuer does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_policy**
> Policy replace_policy(policy_id, policy)

Update a policy

Update a policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy import Policy
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    policy = Policy(
        metadata=MetadataWithId(),
        spec=PolicySpec(
            name="Staging org authentication policy",
            issuer_id="asdfg123hjkl",
            org_id="asdfg123hjkl",
            supported_mfa_methods=["totp","webauthn"],
            default_action="allow_login",
            policy_groups=[
                PolicyGroup(
                    metadata=MetadataWithId(),
                    spec=PolicyGroupSpec(
                        name="name_example",
                        rule_ids=[
                            "123",
                        ],
                    ),
                ),
            ],
            source="Default:1.0.0",
        ),
        status=PolicyStatus(
            associated_issuers=[
                PolicyIssuerRef(
                    issuer_id="123",
                    org_id="123",
                ),
            ],
        ),
    ) # Policy | Policy

    # example passing only required values which don't have defaults set
    try:
        # Update a policy
        api_response = api_instance.replace_policy(policy_id, policy)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **policy** | [**Policy**](Policy.md)| Policy |

### Return type

[**Policy**](Policy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Policy was updated |  -  |
**400** | The request was invalid. |  -  |
**404** | Policy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_policy_rule**
> PolicyRule replace_policy_rule(policy_id, policy_rule_id, policy_rule)

Update a policy rule

Update a policy rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.policy_rule import PolicyRule
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
    api_instance = issuers_api.IssuersApi(api_client)
    policy_id = "1234" # str | Policy Unique identifier
    policy_rule_id = "1234" # str | Policy Rule Unique identifier
    policy_rule = PolicyRule(
        metadata=MetadataWithId(),
        spec=PolicyRuleSpec(
            name="blocked IPs rule",
            action="enroll",
            priority=1,
            org_id="asdfg123hjkl",
            conditions=[
                PolicyCondition(
                    condition_type="type_client_id_list",
                    inverted=False,
                    input_is_list=False,
                    value="my-city-org",
                    operator="equals",
                    field="clients.name",
                ),
            ],
        ),
    ) # PolicyRule | Policy Rule

    # example passing only required values which don't have defaults set
    try:
        # Update a policy rule
        api_response = api_instance.replace_policy_rule(policy_id, policy_rule_id, policy_rule)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_policy_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**| Policy Unique identifier |
 **policy_rule_id** | **str**| Policy Rule Unique identifier |
 **policy_rule** | [**PolicyRule**](PolicyRule.md)| Policy Rule |

### Return type

[**PolicyRule**](PolicyRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Policy Rule was updated |  -  |
**404** | Policy Rule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_root**
> Issuer replace_root(issuer_id, issuer)

Update an issuer

Update an issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer import Issuer
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    issuer = Issuer(
        issuer="issuer_example",
        enabled=True,
        org_id="org_id_example",
        theme_file_id="ASsdq23lsaSSf",
        upstream_redirect_uri="upstream_redirect_uri_example",
        managed_upstreams=[
            ManagedUpstreamIdentityProvider(
                enabled=False,
                prompt_select_account=False,
            ),
        ],
        oidc_upstreams=[
            OIDCUpstreamIdentityProvider(
                name="name_example",
                icon="city-login",
                issuer="issuer_example",
                client_id="client_id_example",
                client_secret="client_secret_example",
                issuer_external_host="issuer_external_host_example",
                username_key="username_key_example",
                email_key="email_key_example",
                email_verification_required=True,
                request_user_info=True,
                user_id_key="user_id_key_example",
                auto_create_status=AutoCreateStatus("active"),
                prompt_mode="auto",
                oidc_flavor="oidc",
                client_authorization_type="federated-credential",
                admin_status=AdminStatus("active"),
                trap_disabled=True,
                operational_status=OperationalStatus(
                    status="good",
                    status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                    generation=1,
                    generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                ),
            ),
        ],
        local_auth_upstreams=[
            LocalAuthUpstreamIdentityProvider(),
        ],
        application_upstreams=[
            ApplicationUpstreamIdentityProvider(),
        ],
        kerberos_upstreams=[
            KerberosUpstreamIdentityProvider(),
        ],
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        saml_state_encryption_key="saml_state_encryption_key_example",
        admin_status=AdminStatus("active"),
        trap_disabled=True,
        operational_status=OperationalStatus(
            status="good",
            status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            generation=1,
            generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
        ),
        parent_issuer="123",
        status=IssuerStatus(
            theme_file_id="ASsdq23lsaSSf",
            operational_status=OperationalStatus(
                status="good",
                status_change_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
                generation=1,
                generation_update_time=dateutil_parser('2022-04-28T15:49:51.23+02:00'),
            ),
            trusted_issuers=[
                TrustedIssuer(
                    issuer="issuer_example",
                    purpose="support_request",
                ),
            ],
        ),
    ) # Issuer | Issuer
    summarize_collection = True # bool | Restrict the results to the summary. Individual collections define what content to include in the summary (optional) if omitted the server will use the default value of True
    org_id = "1234" # str | Organisation Unique identifier (optional)
    force_reconcile_theme = False # bool | Forces reconciling the theme file, even if no change was made (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update an issuer
        api_response = api_instance.replace_root(issuer_id, issuer)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_root: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update an issuer
        api_response = api_instance.replace_root(issuer_id, issuer, summarize_collection=summarize_collection, org_id=org_id, force_reconcile_theme=force_reconcile_theme)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_root: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **issuer** | [**Issuer**](Issuer.md)| Issuer |
 **summarize_collection** | **bool**| Restrict the results to the summary. Individual collections define what content to include in the summary | [optional] if omitted the server will use the default value of True
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **force_reconcile_theme** | **bool**| Forces reconciling the theme file, even if no change was made | [optional]

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Issuer was updated |  -  |
**404** | Issuer does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_upstream_alias**
> UpstreamAlias replace_upstream_alias(issuer_id, upstream_alias_id, upstream_alias)

Update an upstream alias

Update an upstream alias

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_alias import UpstreamAlias
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_alias_id = "1234" # str | upstream alias id
    upstream_alias = UpstreamAlias(
        metadata=MetadataWithId(),
        spec=UpstreamAliasSpec(
            org_id="org_id_example",
            client_id="client_id_example",
            aliases=[
                UpstreamAliasMapping(
                    upstream_provider_name="upstream_provider_name_example",
                    aliased_upstream_provider_names=[
                        "aliased_upstream_provider_names_example",
                    ],
                ),
            ],
        ),
    ) # UpstreamAlias | Issuer upstream alias

    # example passing only required values which don't have defaults set
    try:
        # Update an upstream alias
        api_response = api_instance.replace_upstream_alias(issuer_id, upstream_alias_id, upstream_alias)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_upstream_alias: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_alias_id** | **str**| upstream alias id |
 **upstream_alias** | [**UpstreamAlias**](UpstreamAlias.md)| Issuer upstream alias |

### Return type

[**UpstreamAlias**](UpstreamAlias.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Issuer upstream upstream alias was updated |  -  |
**400** | The request was invalid. Likely a field was missing or incorrectly formatted. |  -  |
**404** | The Issuer does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_upstream_group_mapping**
> UpstreamGroupMapping replace_upstream_group_mapping(issuer_id, upstream_group_mapping_id, upstream_group_mapping)

Update an upstream group mapping

Update an upstream group mapping

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.upstream_group_mapping import UpstreamGroupMapping
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    upstream_group_mapping_id = "1234" # str | upstream group_mapping id
    upstream_group_mapping = UpstreamGroupMapping(
        metadata=MetadataWithId(),
        spec=UpstreamGroupMappingSpec(
            upstream_issuer="https://login.microsoftonline.com/c945d377-ea94-4a7d-9c83-0615e7ff0022/v2.0",
            org_id="asdfg123hjkl",
            group_mappings=[
                UpstreamGroupMappingEntry(
                    priority=1,
                    upstream_group_name="Company Team (.*)",
                    upstream_name_is_a_guid=False,
                    agilicus_group_name="Agilicus {0}",
                    group_org_id="asdfg123hjkl",
                ),
            ],
            excluded_groups=[
                UpstreamGroupExcludedEntry(
                    upstream_group_name="Admin*",
                    upstream_name_is_a_guid=False,
                ),
            ],
        ),
    ) # UpstreamGroupMapping | Issuer upstream group mapping

    # example passing only required values which don't have defaults set
    try:
        # Update an upstream group mapping
        api_response = api_instance.replace_upstream_group_mapping(issuer_id, upstream_group_mapping_id, upstream_group_mapping)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->replace_upstream_group_mapping: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **upstream_group_mapping_id** | **str**| upstream group_mapping id |
 **upstream_group_mapping** | [**UpstreamGroupMapping**](UpstreamGroupMapping.md)| Issuer upstream group mapping |

### Return type

[**UpstreamGroupMapping**](UpstreamGroupMapping.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Issuer upstream group mapping was updated |  -  |
**400** | The request was invalid. Likely a field was missing or incorrectly formatted. |  -  |
**404** | Issuer/Mapping does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reset_service_account**
> Issuer reset_service_account(service_account_reset_body)

Reset the service account for the specified issuer

Reset the service account for the specified issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.issuer import Issuer
from agilicus_api.model.service_account_reset_body import ServiceAccountResetBody
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
    api_instance = issuers_api.IssuersApi(api_client)
    service_account_reset_body = ServiceAccountResetBody(
        issuer_id="123",
        org_id="org_id_example",
    ) # ServiceAccountResetBody | Service Account Reset Body

    # example passing only required values which don't have defaults set
    try:
        # Reset the service account for the specified issuer
        api_response = api_instance.reset_service_account(service_account_reset_body)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->reset_service_account: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_account_reset_body** | [**ServiceAccountResetBody**](ServiceAccountResetBody.md)| Service Account Reset Body |

### Return type

[**Issuer**](Issuer.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully reset issuer service account |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reset_to_default_policy**
> Policy reset_to_default_policy(issuer_id, reset_policy_request)

Reset the current policy to the default policy

Reset the current policy to the default policy. This will create a new policy as the active policy for your organisation. The old policy will still exist with the same policy_id but will be disassociated with this issuer. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy import Policy
from agilicus_api.model.reset_policy_request import ResetPolicyRequest
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    reset_policy_request = ResetPolicyRequest(
        org_id="asdfg123hjkl",
    ) # ResetPolicyRequest | Policy

    # example passing only required values which don't have defaults set
    try:
        # Reset the current policy to the default policy
        api_response = api_instance.reset_to_default_policy(issuer_id, reset_policy_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->reset_to_default_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **reset_policy_request** | [**ResetPolicyRequest**](ResetPolicyRequest.md)| Policy |

### Return type

[**Policy**](Policy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully reset the policy to the default. The new policy for your organisation is returned in the response |  -  |
**400** | An invalid request to reset the policy |  -  |
**404** | A policy does not exist matching that policy_id and org_id |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_policy**
> Policy set_policy(issuer_id, policy_spec)

Set the current policy to the policy sent

Set the current policy to the given policy. This will replace the given issuer's policy with the content from the sent policy. Any ids will be used to link rules together, but be replaced, and any org_ids will be replaced with the org_id of the policy sent. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy import Policy
from agilicus_api.model.policy_spec import PolicySpec
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
    api_instance = issuers_api.IssuersApi(api_client)
    issuer_id = "1234" # str | issuer_id path
    policy_spec = PolicySpec(
        name="Staging org authentication policy",
        issuer_id="asdfg123hjkl",
        org_id="asdfg123hjkl",
        supported_mfa_methods=["totp","webauthn"],
        default_action="allow_login",
        policy_groups=[
            PolicyGroup(
                metadata=MetadataWithId(),
                spec=PolicyGroupSpec(
                    name="name_example",
                    rule_ids=[
                        "123",
                    ],
                ),
            ),
        ],
        source="Default:1.0.0",
    ) # PolicySpec | Policy

    # example passing only required values which don't have defaults set
    try:
        # Set the current policy to the policy sent
        api_response = api_instance.set_policy(issuer_id, policy_spec)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->set_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **issuer_id** | **str**| issuer_id path |
 **policy_spec** | [**PolicySpec**](PolicySpec.md)| Policy |

### Return type

[**Policy**](Policy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully set the policy. The current policy for your organisation is returned in the response |  -  |
**400** | An invalid request to set the policy |  -  |
**404** | A policy does not exist matching that policy_id and org_id |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_upstream**
> validate_upstream(org_id)

Validate upstream issuer

Validate upstream issuer

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import issuers_api
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
    api_instance = issuers_api.IssuersApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    issuer_upstream_url = "issuer_upstream_url_example" # str | upstream upstream url (optional)

    # example passing only required values which don't have defaults set
    try:
        # Validate upstream issuer
        api_instance.validate_upstream(org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->validate_upstream: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Validate upstream issuer
        api_instance.validate_upstream(org_id, issuer_upstream_url=issuer_upstream_url)
    except agilicus_api.ApiException as e:
        print("Exception when calling IssuersApi->validate_upstream: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **issuer_upstream_url** | **str**| upstream upstream url | [optional]

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
**204** | upstream is valid |  -  |
**400** | upstream is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

