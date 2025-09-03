# agilicus_api.ApplicationsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_config**](ApplicationsApi.md#add_config) | **POST** /v2/applications/{app_id}/environments/{env_name}/configs | Add an environment configuration row
[**add_role**](ApplicationsApi.md#add_role) | **POST** /v2/applications/{app_id}/roles | Add a role to the application.
[**add_role_to_rule_entry**](ApplicationsApi.md#add_role_to_rule_entry) | **POST** /v2/applications/{app_id}/role_to_rule_entries | Add a rule to a role in the application.
[**add_rule**](ApplicationsApi.md#add_rule) | **POST** /v2/applications/{app_id}/rules | Add a rule to the application.
[**create_application**](ApplicationsApi.md#create_application) | **POST** /v2/applications | Create an application
[**delete_application**](ApplicationsApi.md#delete_application) | **DELETE** /v2/applications/{app_id} | Remove an application
[**delete_config**](ApplicationsApi.md#delete_config) | **DELETE** /v2/applications/{app_id}/environments/{env_name}/configs/{env_config_id} | Remove an environment configuration
[**delete_role**](ApplicationsApi.md#delete_role) | **DELETE** /v2/applications/{app_id}/roles/{role_id} | Remove a role
[**delete_role_to_rule_entry**](ApplicationsApi.md#delete_role_to_rule_entry) | **DELETE** /v2/applications/{app_id}/role_to_rule_entries/{role_to_rule_entry_id} | Remove a role_to_rule_entry
[**delete_rule**](ApplicationsApi.md#delete_rule) | **DELETE** /v2/applications/{app_id}/rules/{rule_id} | Remove a rule
[**get_all_usage_metrics**](ApplicationsApi.md#get_all_usage_metrics) | **GET** /v1/resources/usage_metrics | Get all resource metrics for the Applications API
[**get_application**](ApplicationsApi.md#get_application) | **GET** /v2/applications/{app_id} | Get a application
[**get_application_usage_metrics**](ApplicationsApi.md#get_application_usage_metrics) | **GET** /v2/applications/usage_metrics | Get application metrics
[**get_config**](ApplicationsApi.md#get_config) | **GET** /v2/applications/{app_id}/environments/{env_name}/configs/{env_config_id} | Get environment configuration
[**get_environment**](ApplicationsApi.md#get_environment) | **GET** /v2/applications/{app_id}/environments/{env_name} | Get an environment
[**get_role**](ApplicationsApi.md#get_role) | **GET** /v2/applications/{app_id}/roles/{role_id} | Get a role
[**get_role_to_rule_entry**](ApplicationsApi.md#get_role_to_rule_entry) | **GET** /v2/applications/{app_id}/role_to_rule_entries/{role_to_rule_entry_id} | Get a role_to_rule_entry
[**get_rule**](ApplicationsApi.md#get_rule) | **GET** /v2/applications/{app_id}/rules/{rule_id} | Get a rule
[**list_application_summaries**](ApplicationsApi.md#list_application_summaries) | **GET** /v2/application_summaries | List application summaries
[**list_applications**](ApplicationsApi.md#list_applications) | **GET** /v2/applications | Get applications
[**list_combined_rules**](ApplicationsApi.md#list_combined_rules) | **GET** /v2/combined_rules | List rules combined by scope or role
[**list_configs**](ApplicationsApi.md#list_configs) | **GET** /v2/applications/{app_id}/environments/{env_name}/configs | Get all environment configuration
[**list_environment_configs_all_apps**](ApplicationsApi.md#list_environment_configs_all_apps) | **GET** /v2/environment_configs | Get all environment configuration for a given organisation.
[**list_role_to_rule_entries**](ApplicationsApi.md#list_role_to_rule_entries) | **GET** /v2/applications/{app_id}/role_to_rule_entries | Get all RoleToRuleEntries
[**list_roles**](ApplicationsApi.md#list_roles) | **GET** /v2/applications/{app_id}/roles | Get all roles
[**list_rules**](ApplicationsApi.md#list_rules) | **GET** /v2/applications/{app_id}/rules | Get all rules
[**list_runtime_status**](ApplicationsApi.md#list_runtime_status) | **GET** /v2/applications/{app_id}/environments/{env_name}/status/runtime_status | Get an environment&#39;s runtime status
[**replace_application**](ApplicationsApi.md#replace_application) | **PUT** /v2/applications/{app_id} | Create or update an application
[**replace_config**](ApplicationsApi.md#replace_config) | **PUT** /v2/applications/{app_id}/environments/{env_name}/configs/{env_config_id} | Update environment configuration
[**replace_environment**](ApplicationsApi.md#replace_environment) | **PUT** /v2/applications/{app_id}/environments/{env_name} | Update an environment
[**replace_role**](ApplicationsApi.md#replace_role) | **PUT** /v2/applications/{app_id}/roles/{role_id} | Update a role
[**replace_role_to_rule_entry**](ApplicationsApi.md#replace_role_to_rule_entry) | **PUT** /v2/applications/{app_id}/role_to_rule_entries/{role_to_rule_entry_id} | Update a role_to_rule_entry
[**replace_rule**](ApplicationsApi.md#replace_rule) | **PUT** /v2/applications/{app_id}/rules/{rule_id} | Update a rule
[**replace_runtime_status**](ApplicationsApi.md#replace_runtime_status) | **PUT** /v2/applications/{app_id}/environments/{env_name}/status/runtime_status | update an environemnt&#39;s runtime status
[**update_patch_application**](ApplicationsApi.md#update_patch_application) | **PATCH** /v2/applications/{app_id} | patch application


# **add_config**
> EnvironmentConfig add_config(app_id, env_name, environment_config)

Add an environment configuration row

Add an environment configuration row

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.environment_config import EnvironmentConfig
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    environment_config = EnvironmentConfig(
        maintenance_org_id="maintenance_org_id_example",
        config_type="configmap_mount",
        mount_domain="mount_domain_example",
        mount_username="mount_username_example",
        mount_password="mount_password_example",
        mount_hostname="mount.example.com",
        mount_share="mount_share_example",
        mount_src_path="mount_src_path_example",
        mount_path="mount_path_example",
        file_store_uri="file_store_uri_example",
        env_config_vars=[
            EnvironmentConfigVar(
                name="_ab2a",
                value="value_example",
            ),
        ],
    ) # EnvironmentConfig | 

    # example passing only required values which don't have defaults set
    try:
        # Add an environment configuration row
        api_response = api_instance.add_config(app_id, env_name, environment_config)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->add_config: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **environment_config** | [**EnvironmentConfig**](EnvironmentConfig.md)|  |

### Return type

[**EnvironmentConfig**](EnvironmentConfig.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New environment config row created |  -  |
**409** | Environment configuration requested already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_role**
> RoleV2 add_role(app_id, role_v2)

Add a role to the application.

Add a role to the application.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.role_v2 import RoleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_v2 = RoleV2(
        metadata=MetadataWithId(),
        spec=RoleSpec(
            app_id="123",
            name="owner",
            comments="This role allows access to all read-only endpoints of the application. Assign this role to anybody who needs to be able to interact with the application in a read-only fashion, such as an auditor.",
            included=[
                IncludedRole(
                    role_id="123",
                ),
            ],
            org_id="123",
        ),
    ) # RoleV2 | 

    # example passing only required values which don't have defaults set
    try:
        # Add a role to the application.
        api_response = api_instance.add_role(app_id, role_v2)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->add_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_v2** | [**RoleV2**](RoleV2.md)|  |

### Return type

[**RoleV2**](RoleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New role created |  -  |
**409** | A role of this name already exists in the application. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_role_to_rule_entry**
> RoleToRuleEntry add_role_to_rule_entry(app_id, role_to_rule_entry)

Add a rule to a role in the application.

Add a rule to a role in the application.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.role_to_rule_entry import RoleToRuleEntry
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_to_rule_entry = RoleToRuleEntry(
        metadata=MetadataWithId(),
        spec=RoleToRuleEntrySpec(
            role_id="123",
            rule_id="123",
            app_id="123",
            org_id="123",
            included=True,
        ),
    ) # RoleToRuleEntry | 

    # example passing only required values which don't have defaults set
    try:
        # Add a rule to a role in the application.
        api_response = api_instance.add_role_to_rule_entry(app_id, role_to_rule_entry)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->add_role_to_rule_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_to_rule_entry** | [**RoleToRuleEntry**](RoleToRuleEntry.md)|  |

### Return type

[**RoleToRuleEntry**](RoleToRuleEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New role_to_rule_entry created |  -  |
**409** | The rule is already mapped to the role |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_rule**
> RuleV2 add_rule(app_id, rule_v2)

Add a rule to the application.

Add a rule to the application.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.rule_v2 import RuleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    rule_v2 = RuleV2(
        metadata=MetadataWithId(),
        spec=RuleSpec(
            app_id="123",
            comments="This rule allows access to all static content of the application for any user, even if they are not authenticated.",
            condition=HttpRule(
                rule_type="rule_type_example",
                condition_type="http_rule_condition",
                methods=["get"],
                path_regex="/.*",
                path_template=TemplatePath(
                    template="/collection/{guid}/subcollection/{sub_guid}",
                    prefix=False,
                ),
                query_parameters=[
                    RuleQueryParameter(
                        name="name_example",
                        exact_match="exact_match_example",
                        match_type="match_type_example",
                    ),
                ],
                body=RuleQueryBody(
                    json=[
                        RuleQueryBodyJSON(
                            name="name_example",
                            exact_match="exact_match_example",
                            match_type="string",
                            pointer="/foo/0/a~1b/2",
                        ),
                    ],
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
            org_id="123",
            scope=RuleScopeEnum("anyone"),
        ),
    ) # RuleV2 | 

    # example passing only required values which don't have defaults set
    try:
        # Add a rule to the application.
        api_response = api_instance.add_rule(app_id, rule_v2)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->add_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **rule_v2** | [**RuleV2**](RuleV2.md)|  |

### Return type

[**RuleV2**](RuleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New rule created |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_application**
> Application create_application(application)

Create an application

Create an application according to spec

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.application import Application
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
    api_instance = applications_api.ApplicationsApi(api_client)
    application = Application(
        name="z",
        description="description_example",
        category="category_example",
        image="image_example",
        image_username="image_username_example",
        image_password="image_password_example",
        image_credentials_type="basic_auth",
        environments=[
            Environment(
                name="name_example",
                maintenance_org_id="maintenance_org_id_example",
                domain_aliases=[
                    "uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
                ],
                version_tag="version_tag_example",
                config_mount_path="config_mount_path_example",
                config_as_mount="config_as_mount_example",
                config_as_env="config_as_env_example",
                secrets_mount_path="secrets_mount_path_example",
                secrets_as_mount="secrets_as_mount_example",
                secrets_as_env="secrets_as_env_example",
                serverless_image="serverless_image_example",
                status=EnvironmentStatus(
                    runtime_status=RuntimeStatus(
                        overall_status="good",
                        running_replicas=2,
                        error_message="CrashLoopBackoff",
                        restarts=5,
                        cpu=0.6,
                        memory=45.2,
                        last_apply_time=dateutil_parser('2002-10-02T10:00:00-05:00'),
                        running_image="cr.agilicus.com/applications/iomad:v1.13.0",
                        running_hash="sha256:2fb759c1adfe40863b89a4076111af8f210e7342d2240f09b08fc445b357112e",
                        org_id="123",
                    ),
                ),
                application_configs=ApplicationConfig(
                    authentication_config=ApplicationAuthenticationConfig(
                        application_handles_authentication=False,
                        session_secret="Gns5ZPCvXGjzrtB672HAxfoSQ0dmqriSgiQf6uEQSBU=",
                        upstream=OIDCProxyUpstreamAuthentication(
                            ntlm=OIDCProxyUpstreamNTLM(
                                ntlm_passthrough=False,
                            ),
                        ),
                    ),
                    oidc_config=OIDCProxyConfig(
                        headers=OIDCProxyHeader(
                            domain_substitution=OIDCProxyDomainSubstitution(
                                standard_headers=OIDCProxyStandardHeader(
                                    location=True,
                                    origin=True,
                                    host=True,
                                    set_cookie_header=True,
                                    cookie=True,
                                ),
                                other_headers=[
                                    OIDCProxyHeaderMapping(
                                        name="Accept-Encoding",
                                        value="*",
                                    ),
                                ],
                                path=True,
                            ),
                            header_overrides=OIDCProxyHeaderOverride(
                                request=OIDCProxyHeaderUserConfig(
                                    set=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    add=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    remove=[
                                        OIDCProxyHeaderName(
                                            name="name_example",
                                        ),
                                    ],
                                    remove_match=[
                                        OIDCProxyHeaderMatch(
                                            name_exact="name_exact_example",
                                            value_regex="value_regex_example",
                                        ),
                                    ],
                                    filters=[
                                        OIDCProxyHeaderRewriteFilter(
                                            rewrite_type="rewrite_type_example",
                                        ),
                                    ],
                                    replace=[
                                        OIDCProxyHeaderReplace(
                                            old_name="old_name_example",
                                            new_name="new_name_example",
                                        ),
                                    ],
                                ),
                                response=OIDCProxyHeaderUserConfig(
                                    set=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    add=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    remove=[
                                        OIDCProxyHeaderName(
                                            name="name_example",
                                        ),
                                    ],
                                    remove_match=[
                                        OIDCProxyHeaderMatch(
                                            name_exact="name_exact_example",
                                            value_regex="value_regex_example",
                                        ),
                                    ],
                                    filters=[
                                        OIDCProxyHeaderRewriteFilter(
                                            rewrite_type="rewrite_type_example",
                                        ),
                                    ],
                                    replace=[
                                        OIDCProxyHeaderReplace(
                                            old_name="old_name_example",
                                            new_name="new_name_example",
                                        ),
                                    ],
                                ),
                            ),
                        ),
                        domain_mapping=OIDCProxyDomainMapping(
                            primary_external_name="app-1.cloud.egov.city",
                            primary_internal_name="app-1.internal",
                            use_service_hostname=True,
                            use_recursive_replacement_system=False,
                            other_mappings=[
                                OIDCProxyDomainNameMapping(
                                    internal_name="local_test_app",
                                    external_name="app-1",
                                ),
                            ],
                        ),
                        auth=OIDCAuthConfig(
                            auth_enabled=True,
                            client_id="admin-portal",
                            issuer="https://auth.cloud.egov.city",
                            logout_url="/login/logout.cfm",
                            scopes=[
                                OIDCProxyScope(
                                    name="urn:agilicus:app:app-1:owner",
                                ),
                            ],
                            path_config=OIDCAuthPathConfig(
                                included_paths=[
                                    OIDCAuthURI(
                                        path="/logout",
                                    ),
                                ],
                                excluded_paths=[
                                    OIDCAuthURI(
                                        path="/logout",
                                    ),
                                ],
                            ),
                            redirect_after_signin_path="/somepath/index.html",
                            redirect_subpath="/somepath/foo",
                        ),
                        content_manipulation=OIDCProxyContentManipulation(
                            media_types=[
                                OIDCContentType(
                                    name="text/css",
                                ),
                            ],
                        ),
                        upstream_config=OIDCProxyUpstreamConfig(
                            scheme="https",
                            hostname="httpbin.org",
                            port=1,
                        ),
                    ),
                    security=ApplicationSecurity(
                        http=HTTPSecuritySettings(
                            csp=CSPSettings(
                                enabled=True,
                                mode="enforce",
                                directives=[
                                    CSPDirective(
                                        name="default-src",
                                        values=[
                                            "https:",
                                        ],
                                    ),
                                ],
                            ),
                            cors=CORSSettings(
                                enabled=True,
                                mode="overwrite",
                                origin_matching="me",
                                allow_resource_origins=True,
                                allow_origins=[
                                    CORSOrigin(
                                        exact="https://other-site.agilicus.cloud",
                                    ),
                                ],
                                allow_methods=[
                                    "POST",
                                ],
                                allow_headers=[
                                    "Destination",
                                ],
                                expose_headers=[
                                    "Location",
                                ],
                                max_age_seconds=3600,
                                allow_credentials=True,
                            ),
                            hsts=HSTSSettings(
                                enabled=True,
                                max_age_seconds=63072000,
                                include_sub_domains=False,
                                preload=True,
                            ),
                            xss_protection=XSSSettings(
                                enabled=True,
                                mode="block",
                                report_uri="https://my-site.agilicus.cloud/xss-reports",
                            ),
                            certificate_transparency=CertificateTransparencySettings(
                                enabled=True,
                                report_uri="https://my-site.agilicus.cloud/ct-reports",
                                enforce=True,
                                max_age_seconds=63072000,
                            ),
                            frame_options=FrameOptionsSettings(
                                enabled=True,
                                mode="deny",
                                override="ALLOW-FROM https://my-site.agilicus.cloud/",
                            ),
                            content_type_options=ContentTypeOptionsSettings(
                                enabled=True,
                                mode="nosniff",
                                override="SomeCustomSetting",
                            ),
                            permitted_cross_domain_policies=PermittedCrossDomainPoliciesSettings(
                                enabled=True,
                                mode="clear",
                                override="master-only",
                            ),
                            coep=CrossOriginEmbedderPolicySettings(
                                enabled=True,
                                mode="unsafe_none",
                                override="some-custom-setting",
                            ),
                            coop=CrossOriginOpenerPolicySettings(
                                enabled=True,
                                mode="unsafe_none",
                                override="some-custom-setting",
                            ),
                            corp=CrossOriginResourcePolicySettings(
                                enabled=True,
                                mode="same_site",
                                override="some-custom-setting",
                            ),
                            referrer_policy=ReferrerPolicySettings(
                                enabled=True,
                                mode="no_referrer",
                                override="some-custom-setting",
                            ),
                        ),
                    ),
                    additional_context=ApplicationAdditionalContext(
                        include_user_context_headers=False,
                    ),
                ),
                name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
                migrated_app_id="migrated_app_id_example",
                proxy_location="in_cloud",
            ),
        ],
        org_id="org_id_example",
        contact_email="contact_email_example",
        monitoring_config=ApplicationMonitoringConfig(
            port=1,
            path="/metrics",
        ),
        port=1,
        healthcheck_uri="healthcheck_uri_example",
        roles=RoleList([
            Role(
                name="name_example",
                rules=[
                    Rule(
                        host="host_example",
                        name="rules.add",
                        method="get",
                        path="/.*",
                        query_parameters=[
                            RuleQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                                match_type="match_type_example",
                            ),
                        ],
                        body=RuleQueryBody(
                            json=[
                                RuleQueryBodyJSON(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]),
        roles_config=RolesConfig(
            roles=[
                RoleConfig(
                    role_name="owner",
                    default=False,
                    description="Provides full access to the the file share.",
                    included_roles=[
                        "included_roles_example",
                    ],
                ),
            ],
        ),
        rules_config=RulesConfig(
            rules=[
                RuleConfig(
                    name="-",
                    roles=[
                        "roles_example",
                    ],
                    excluded_roles=[
                        "excluded_roles_example",
                    ],
                    comments="This rule allows access to all static content of the application for any user, even if they are not authenticated.",
                    condition=HttpRule(
                        rule_type="rule_type_example",
                        condition_type="http_rule_condition",
                        methods=["get"],
                        path_regex="/.*",
                        path_template=TemplatePath(
                            template="/collection/{guid}/subcollection/{sub_guid}",
                            prefix=False,
                        ),
                        query_parameters=[
                            RuleQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                                match_type="match_type_example",
                            ),
                        ],
                        body=RuleQueryBody(
                            json=[
                                RuleQueryBodyJSON(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
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
                    scope=RuleScopeEnum("anyone"),
                    extended_condition=RuleCondition(
                        negated=False,
                        condition=RuleConditionBase(
                            condition_type="CompoundRuleCondition",
                            condition_list=[
                                RuleCondition(),
                            ],
                            list_type="cnf",
                        ),
                    ),
                    priority=1,
                    actions=[
                        RuleAction(
                            action="allow",
                            log_message="rule-1-hit",
                            path="/subpath",
                        ),
                    ],
                ),
            ],
            rule_set_components=[
                RuleSetComponent(
                    parent_rule_name="-",
                    child_rule_name="-",
                    priority=1,
                ),
            ],
        ),
        definitions=[
            Definition(
                key="key_example",
                value="value_example",
            ),
        ],
        assignments=[
            ApplicationAssignment(
                org_id="asd901laskbh",
                environment_name="production",
            ),
        ],
        owned=True,
        maintained=True,
        assigned=True,
        published="no",
        default_role_id="AcaSL40fs22l4Dr4XoAd5y",
        icon_url="icon_url_example",
        display_info=DisplayInfo(
            icons=[
                Icon(
                    uri="https://storage.googleapis.com/agilicus/logo.svg",
                    purposes=[
                        IconPurpose("agilicus-launcher"),
                    ],
                    dimensions=IconDimensions(
                        width=32,
                        height=32,
                    ),
                ),
            ],
            hide="no",
        ),
        location="hosted",
        service_account_required=True,
        application_type="user_defined",
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        workload_config=WorkloadConfiguration(
            env_config_vars=[
                EnvironmentConfigVar(
                    name="_ab2a",
                    value="value_example",
                ),
            ],
        ),
        admin_state=ApplicationStateSelector("active"),
        alternate_mode_setting=AlternateModeSetting(
            learning_mode=LearningModeSpec(
                expiry_time=dateutil_parser('2019-05-16T19:11:18Z'),
            ),
            diagnostic_mode=True,
        ),
        launchers=[
            "123",
        ],
    ) # Application | 

    # example passing only required values which don't have defaults set
    try:
        # Create an application
        api_response = api_instance.create_application(application)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->create_application: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application** | [**Application**](Application.md)|  |

### Return type

[**Application**](Application.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New application created |  -  |
**409** | Application already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_application**
> delete_application(app_id)

Remove an application

Remove an application

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove an application
        api_instance.delete_application(app_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_application: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove an application
        api_instance.delete_application(app_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_application: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
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
**204** | Application was deleted |  -  |
**404** | Application does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_config**
> delete_config(app_id, env_name, env_config_id, maintenance_org_id)

Remove an environment configuration

Remove an environment configuration

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    env_config_id = "G" # str | environment configuration id
    maintenance_org_id = "G" # str | Organisation unique identifier for an object being maintained by an organisation different than it. 

    # example passing only required values which don't have defaults set
    try:
        # Remove an environment configuration
        api_instance.delete_config(app_id, env_name, env_config_id, maintenance_org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_config: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **env_config_id** | **str**| environment configuration id |
 **maintenance_org_id** | **str**| Organisation unique identifier for an object being maintained by an organisation different than it.  |

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
**204** | Environment configuration was deleted |  -  |
**404** | Environment configuration does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_role**
> delete_role(app_id, role_id)

Remove a role

Remove a role

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_id = "Absadal2" # str | The id of a role
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove a role
        api_instance.delete_role(app_id, role_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_role: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove a role
        api_instance.delete_role(app_id, role_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_id** | **str**| The id of a role |
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
**204** | Role was deleted |  -  |
**404** | The Role does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_role_to_rule_entry**
> delete_role_to_rule_entry(app_id, role_to_rule_entry_id)

Remove a role_to_rule_entry

Remove a role_to_rule_entry

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_to_rule_entry_id = "Absadal2" # str | The id of a role to rule entry
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove a role_to_rule_entry
        api_instance.delete_role_to_rule_entry(app_id, role_to_rule_entry_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_role_to_rule_entry: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove a role_to_rule_entry
        api_instance.delete_role_to_rule_entry(app_id, role_to_rule_entry_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_role_to_rule_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_to_rule_entry_id** | **str**| The id of a role to rule entry |
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
**204** | RoleToRuleEntry was deleted |  -  |
**404** | The RoleToRuleEntry does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_rule**
> delete_rule(app_id, rule_id)

Remove a rule

Remove a rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    rule_id = "Absadal2" # str | The id of a rule
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove a rule
        api_instance.delete_rule(app_id, rule_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove a rule
        api_instance.delete_rule(app_id, rule_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->delete_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **rule_id** | **str**| The id of a rule |
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
**204** | Rule was deleted |  -  |
**404** | The Rule does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_usage_metrics**
> UsageMetrics get_all_usage_metrics(org_id)

Get all resource metrics for the Applications API

Retrieves all resource metrics for the Applications API for a specified the org_id. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.usage_metrics import UsageMetrics
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
    api_instance = applications_api.ApplicationsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get all resource metrics for the Applications API
        api_response = api_instance.get_all_usage_metrics(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_all_usage_metrics: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all resource metrics for the Applications API
        api_response = api_instance.get_all_usage_metrics(org_id, org_ids=org_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_all_usage_metrics: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]

### Return type

[**UsageMetrics**](UsageMetrics.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return application resource metrics |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_application**
> Application get_application(app_id)

Get a application

Get a application

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.application import Application
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)
    assigned_org_id = "G" # str | Organisation unique identifier for an assigned object (optional)
    include_migrated_environments = True # bool | Application environments have now been migrated to utilize their own application. While upgrading these environments to their own application, existing clients may still request the usage of multiple environments within an application. As such, the default behavior for retrieval of applications is to not include these new migrated environment applications.  (optional)
    get_scopes = False # bool | In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. (optional) if omitted the server will use the default value of False

    # example passing only required values which don't have defaults set
    try:
        # Get a application
        api_response = api_instance.get_application(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_application: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a application
        api_response = api_instance.get_application(app_id, org_id=org_id, assigned_org_id=assigned_org_id, include_migrated_environments=include_migrated_environments, get_scopes=get_scopes)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_application: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **assigned_org_id** | **str**| Organisation unique identifier for an assigned object | [optional]
 **include_migrated_environments** | **bool**| Application environments have now been migrated to utilize their own application. While upgrading these environments to their own application, existing clients may still request the usage of multiple environments within an application. As such, the default behavior for retrieval of applications is to not include these new migrated environment applications.  | [optional]
 **get_scopes** | **bool**| In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. | [optional] if omitted the server will use the default value of False

### Return type

[**Application**](Application.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return Application |  -  |
**404** | Application does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_application_usage_metrics**
> UsageMetric get_application_usage_metrics(org_id)

Get application metrics

Retrieves all application metrics related to the org_id. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.usage_metric import UsageMetric
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
    api_instance = applications_api.ApplicationsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier

    # example passing only required values which don't have defaults set
    try:
        # Get application metrics
        api_response = api_instance.get_application_usage_metrics(org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_application_usage_metrics: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier |

### Return type

[**UsageMetric**](UsageMetric.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return application Usage metrics |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_config**
> EnvironmentConfig get_config(app_id, env_name, env_config_id, maintenance_org_id)

Get environment configuration

Retrieve environment configuration 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.environment_config import EnvironmentConfig
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    env_config_id = "G" # str | environment configuration id
    maintenance_org_id = "G" # str | Organisation unique identifier for an object being maintained by an organisation different than it. 

    # example passing only required values which don't have defaults set
    try:
        # Get environment configuration
        api_response = api_instance.get_config(app_id, env_name, env_config_id, maintenance_org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_config: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **env_config_id** | **str**| environment configuration id |
 **maintenance_org_id** | **str**| Organisation unique identifier for an object being maintained by an organisation different than it.  |

### Return type

[**EnvironmentConfig**](EnvironmentConfig.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Environment configuration successfully retrieved. |  -  |
**403** | Reading this environment is not permitted. This could happen due to insufficient permissions within your organisation.  |  -  |
**404** | The Environment configuration does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_environment**
> Environment get_environment(app_id, env_name, org_id)

Get an environment

This allows an environment maintainer to get an environment they maintain. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.environment import Environment
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    org_id = "G" # str | Organisation unique identifier
    get_scopes = False # bool | In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. (optional) if omitted the server will use the default value of False

    # example passing only required values which don't have defaults set
    try:
        # Get an environment
        api_response = api_instance.get_environment(app_id, env_name, org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_environment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get an environment
        api_response = api_instance.get_environment(app_id, env_name, org_id, get_scopes=get_scopes)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_environment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **org_id** | **str**| Organisation unique identifier |
 **get_scopes** | **bool**| In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. | [optional] if omitted the server will use the default value of False

### Return type

[**Environment**](Environment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Environment successfully retrieved. |  -  |
**403** | Reading this environment is not permitted. This could happen due to insufficient permissions within your organisation.  |  -  |
**404** | Environment does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_role**
> RoleV2 get_role(app_id, role_id)

Get a role

Retrieves a given role by ID 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.role_v2 import RoleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_id = "Absadal2" # str | The id of a role
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a role
        api_response = api_instance.get_role(app_id, role_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_role: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a role
        api_response = api_instance.get_role(app_id, role_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_id** | **str**| The id of a role |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**RoleV2**](RoleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Role successfully retrieved. |  -  |
**404** | Role does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_role_to_rule_entry**
> RoleToRuleEntry get_role_to_rule_entry(app_id, role_to_rule_entry_id)

Get a role_to_rule_entry

Retrieves a given role_to_rule_entry by ID 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.role_to_rule_entry import RoleToRuleEntry
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_to_rule_entry_id = "Absadal2" # str | The id of a role to rule entry
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a role_to_rule_entry
        api_response = api_instance.get_role_to_rule_entry(app_id, role_to_rule_entry_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_role_to_rule_entry: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a role_to_rule_entry
        api_response = api_instance.get_role_to_rule_entry(app_id, role_to_rule_entry_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_role_to_rule_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_to_rule_entry_id** | **str**| The id of a role to rule entry |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**RoleToRuleEntry**](RoleToRuleEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | RoleToRuleEntry successfully retrieved. |  -  |
**404** | RoleToRuleEntry does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_rule**
> RuleV2 get_rule(app_id, rule_id)

Get a rule

Retrieves a given rule by ID 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.rule_v2 import RuleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    rule_id = "Absadal2" # str | The id of a rule
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a rule
        api_response = api_instance.get_rule(app_id, rule_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a rule
        api_response = api_instance.get_rule(app_id, rule_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->get_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **rule_id** | **str**| The id of a rule |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**RuleV2**](RuleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Rule successfully retrieved. |  -  |
**404** | Rule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_application_summaries**
> ListApplicationSummaryResponse list_application_summaries()

List application summaries

Retrieve all application summaries corresponding to the provided parameters. One summary will exist per organisation assigned to the application. If a single org id is provided in the `org_id` parameter, then all assignments for all applications owned by that org will be listed. If a list of org ids are provided via the `assigned_org_ids` parameter, then the assignments will be constrained to ones for those org ids. Note that these two org id parameters can work together. One constrains the applications, and the other the assignments, so the combination of the two could be used to show a subset of the assignments for a given organisation's applications. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_application_summary_response import ListApplicationSummaryResponse
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
    api_instance = applications_api.ApplicationsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    assigned_org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The asssigned org ids to search for. Each org will be searched for independently. (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List application summaries
        api_response = api_instance.list_application_summaries(org_id=org_id, assigned_org_ids=assigned_org_ids, resource_id=resource_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_application_summaries: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **assigned_org_ids** | **[str]**| The asssigned org ids to search for. Each org will be searched for independently. | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListApplicationSummaryResponse**](ListApplicationSummaryResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ApplicationSummary list successfully retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_applications**
> ListApplicationsResponse list_applications()

Get applications

Retrieves all applications related to the org_id. Different types of relationship may be queried by setting the appropriate flags:   - assigned: Has an Environment assigned to the organisation.   - owned: Owned by the organisation.   - maintained: Has an Environment maintained by the organisation. Any combination of the relationship flags may be set. Note that if the organisation does not own the Application, but maintains or is assigned an environment only those assignments and environments for the querying organisation will be shown. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_applications_response import ListApplicationsResponse
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
    api_instance = applications_api.ApplicationsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    assigned_org_id = "G" # str | Organisation unique identifier for an assigned object (optional)
    maintained = True # bool | Query for Applications maintained by the `org_id`. These are Applications which have an Environment whose `maintenance_org_id` is the `org_id`.  (optional)
    assigned = True # bool | Query for Applications assigned to the `org_id`. These are Applications with at least one Environment assigned to the `org_id`.  (optional)
    owned = True # bool | Query for Applications owned by the `org_id`. (optional)
    updated_since = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime | query since updated (optional)
    show_status = True # bool | Whether the return value should include the status for included objects. If false the query may run faster but will not include status information.  (optional) if omitted the server will use the default value of False
    application_type = ["user_defined"] # [str] | Query based on the application type. Multiple values are ORed together.  (optional) if omitted the server will use the default value of ["user_defined"]
    include_migrated_environments = True # bool | Application environments have now been migrated to utilize their own application. While upgrading these environments to their own application, existing clients may still request the usage of multiple environments within an application. As such, the default behavior for retrieval of applications is to not include these new migrated environment applications.  (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get applications
        api_response = api_instance.list_applications(org_id=org_id, assigned_org_id=assigned_org_id, maintained=maintained, assigned=assigned, owned=owned, updated_since=updated_since, show_status=show_status, application_type=application_type, include_migrated_environments=include_migrated_environments, resource_id=resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_applications: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **assigned_org_id** | **str**| Organisation unique identifier for an assigned object | [optional]
 **maintained** | **bool**| Query for Applications maintained by the &#x60;org_id&#x60;. These are Applications which have an Environment whose &#x60;maintenance_org_id&#x60; is the &#x60;org_id&#x60;.  | [optional]
 **assigned** | **bool**| Query for Applications assigned to the &#x60;org_id&#x60;. These are Applications with at least one Environment assigned to the &#x60;org_id&#x60;.  | [optional]
 **owned** | **bool**| Query for Applications owned by the &#x60;org_id&#x60;. | [optional]
 **updated_since** | **datetime**| query since updated | [optional]
 **show_status** | **bool**| Whether the return value should include the status for included objects. If false the query may run faster but will not include status information.  | [optional] if omitted the server will use the default value of False
 **application_type** | **[str]**| Query based on the application type. Multiple values are ORed together.  | [optional] if omitted the server will use the default value of ["user_defined"]
 **include_migrated_environments** | **bool**| Application environments have now been migrated to utilize their own application. While upgrading these environments to their own application, existing clients may still request the usage of multiple environments within an application. As such, the default behavior for retrieval of applications is to not include these new migrated environment applications.  | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]

### Return type

[**ListApplicationsResponse**](ListApplicationsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return applications |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_combined_rules**
> ListCombinedRulesResponse list_combined_rules()

List rules combined by scope or role

Retrieve all role_to_rule_entries for an application. If assigned is true, this will list all role_to_rule_entries for applications assigned to the given org_id 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.rule_scope_enum import RuleScopeEnum
from agilicus_api.model.list_combined_rules_response import ListCombinedRulesResponse
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
    api_instance = applications_api.ApplicationsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    scopes = [
        RuleScopeEnum("["anyone"]"),
    ] # [RuleScopeEnum] | The scopes of the rules to search for. Multiple values are ORed together. (optional)
    app_id = "G" # str | Application unique identifier (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    assigned = True # bool | Query for Applications assigned to the `org_id`. These are Applications with at least one Environment assigned to the `org_id`.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List rules combined by scope or role
        api_response = api_instance.list_combined_rules(org_id=org_id, scopes=scopes, app_id=app_id, limit=limit, assigned=assigned)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_combined_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **scopes** | [**[RuleScopeEnum]**](RuleScopeEnum.md)| The scopes of the rules to search for. Multiple values are ORed together. | [optional]
 **app_id** | **str**| Application unique identifier | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **assigned** | **bool**| Query for Applications assigned to the &#x60;org_id&#x60;. These are Applications with at least one Environment assigned to the &#x60;org_id&#x60;.  | [optional]

### Return type

[**ListCombinedRulesResponse**](ListCombinedRulesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CombinedRules were successfully retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_configs**
> ListConfigsResponse list_configs(app_id, env_name, maintenance_org_id)

Get all environment configuration

Retrieve all environment configuration 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_configs_response import ListConfigsResponse
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    maintenance_org_id = "G" # str | Organisation unique identifier for an object being maintained by an organisation different than it. 

    # example passing only required values which don't have defaults set
    try:
        # Get all environment configuration
        api_response = api_instance.list_configs(app_id, env_name, maintenance_org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_configs: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **maintenance_org_id** | **str**| Organisation unique identifier for an object being maintained by an organisation different than it.  |

### Return type

[**ListConfigsResponse**](ListConfigsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Environment configuration successfully retrieved. |  -  |
**403** | Reading this environment is not permitted. This could happen due to insufficient permissions within your organisation.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_environment_configs_all_apps**
> ListEnvironmentConfigsResponse list_environment_configs_all_apps(maintenance_org_id)

Get all environment configuration for a given organisation.

Retrieve all environment configuration for a organisation. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_environment_configs_response import ListEnvironmentConfigsResponse
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
    api_instance = applications_api.ApplicationsApi(api_client)
    maintenance_org_id = "G" # str | Organisation unique identifier for an object being maintained by an organisation different than it. 
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    try:
        # Get all environment configuration for a given organisation.
        api_response = api_instance.list_environment_configs_all_apps(maintenance_org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_environment_configs_all_apps: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all environment configuration for a given organisation.
        api_response = api_instance.list_environment_configs_all_apps(maintenance_org_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_environment_configs_all_apps: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **maintenance_org_id** | **str**| Organisation unique identifier for an object being maintained by an organisation different than it.  |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListEnvironmentConfigsResponse**](ListEnvironmentConfigsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Environment configuration successfully retrieved. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_role_to_rule_entries**
> ListRoleToRuleEntries list_role_to_rule_entries(app_id)

Get all RoleToRuleEntries

Retrieve all role_to_rule_entries for an application 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_role_to_rule_entries import ListRoleToRuleEntries
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    try:
        # Get all RoleToRuleEntries
        api_response = api_instance.list_role_to_rule_entries(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_role_to_rule_entries: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all RoleToRuleEntries
        api_response = api_instance.list_role_to_rule_entries(app_id, org_id=org_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_role_to_rule_entries: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListRoleToRuleEntries**](ListRoleToRuleEntries.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | RoleToRuleEntries successfully retrieved. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_roles**
> ListRoles list_roles(app_id)

Get all roles

Retrieve all roles for an application 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.list_roles import ListRoles
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    try:
        # Get all roles
        api_response = api_instance.list_roles(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_roles: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all roles
        api_response = api_instance.list_roles(app_id, org_id=org_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_roles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListRoles**](ListRoles.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Roles successfully retrieved. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_rules**
> ListRules list_rules(app_id)

Get all rules

Retrieve all rules for an application 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.rule_scope_enum import RuleScopeEnum
from agilicus_api.model.list_rules import ListRules
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_id = "1234" # str | Organisation Unique identifier (optional)
    scope = RuleScopeEnum("anyone") # RuleScopeEnum | The scope of the rules to search for (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    try:
        # Get all rules
        api_response = api_instance.list_rules(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_rules: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all rules
        api_response = api_instance.list_rules(app_id, org_id=org_id, scope=scope, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **scope** | **RuleScopeEnum**| The scope of the rules to search for | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListRules**](ListRules.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Rules successfully retrieved. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_runtime_status**
> RuntimeStatus list_runtime_status(app_id, env_name, org_id)

Get an environment's runtime status

Get an environment's runtime status 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.runtime_status import RuntimeStatus
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    org_id = "G" # str | Organisation unique identifier

    # example passing only required values which don't have defaults set
    try:
        # Get an environment's runtime status
        api_response = api_instance.list_runtime_status(app_id, env_name, org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->list_runtime_status: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **org_id** | **str**| Organisation unique identifier |

### Return type

[**RuntimeStatus**](RuntimeStatus.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Environment status successfully retrieved. |  -  |
**403** | Reading this environment status is not permitted. This could happen due to insufficient permissions within your organisation.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_application**
> Application replace_application(app_id)

Create or update an application

Create or update an application

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.application import Application
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    application = Application(
        name="z",
        description="description_example",
        category="category_example",
        image="image_example",
        image_username="image_username_example",
        image_password="image_password_example",
        image_credentials_type="basic_auth",
        environments=[
            Environment(
                name="name_example",
                maintenance_org_id="maintenance_org_id_example",
                domain_aliases=[
                    "uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
                ],
                version_tag="version_tag_example",
                config_mount_path="config_mount_path_example",
                config_as_mount="config_as_mount_example",
                config_as_env="config_as_env_example",
                secrets_mount_path="secrets_mount_path_example",
                secrets_as_mount="secrets_as_mount_example",
                secrets_as_env="secrets_as_env_example",
                serverless_image="serverless_image_example",
                status=EnvironmentStatus(
                    runtime_status=RuntimeStatus(
                        overall_status="good",
                        running_replicas=2,
                        error_message="CrashLoopBackoff",
                        restarts=5,
                        cpu=0.6,
                        memory=45.2,
                        last_apply_time=dateutil_parser('2002-10-02T10:00:00-05:00'),
                        running_image="cr.agilicus.com/applications/iomad:v1.13.0",
                        running_hash="sha256:2fb759c1adfe40863b89a4076111af8f210e7342d2240f09b08fc445b357112e",
                        org_id="123",
                    ),
                ),
                application_configs=ApplicationConfig(
                    authentication_config=ApplicationAuthenticationConfig(
                        application_handles_authentication=False,
                        session_secret="Gns5ZPCvXGjzrtB672HAxfoSQ0dmqriSgiQf6uEQSBU=",
                        upstream=OIDCProxyUpstreamAuthentication(
                            ntlm=OIDCProxyUpstreamNTLM(
                                ntlm_passthrough=False,
                            ),
                        ),
                    ),
                    oidc_config=OIDCProxyConfig(
                        headers=OIDCProxyHeader(
                            domain_substitution=OIDCProxyDomainSubstitution(
                                standard_headers=OIDCProxyStandardHeader(
                                    location=True,
                                    origin=True,
                                    host=True,
                                    set_cookie_header=True,
                                    cookie=True,
                                ),
                                other_headers=[
                                    OIDCProxyHeaderMapping(
                                        name="Accept-Encoding",
                                        value="*",
                                    ),
                                ],
                                path=True,
                            ),
                            header_overrides=OIDCProxyHeaderOverride(
                                request=OIDCProxyHeaderUserConfig(
                                    set=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    add=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    remove=[
                                        OIDCProxyHeaderName(
                                            name="name_example",
                                        ),
                                    ],
                                    remove_match=[
                                        OIDCProxyHeaderMatch(
                                            name_exact="name_exact_example",
                                            value_regex="value_regex_example",
                                        ),
                                    ],
                                    filters=[
                                        OIDCProxyHeaderRewriteFilter(
                                            rewrite_type="rewrite_type_example",
                                        ),
                                    ],
                                    replace=[
                                        OIDCProxyHeaderReplace(
                                            old_name="old_name_example",
                                            new_name="new_name_example",
                                        ),
                                    ],
                                ),
                                response=OIDCProxyHeaderUserConfig(
                                    set=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    add=[
                                        OIDCProxyHeaderMapping(
                                            name="Accept-Encoding",
                                            value="*",
                                        ),
                                    ],
                                    remove=[
                                        OIDCProxyHeaderName(
                                            name="name_example",
                                        ),
                                    ],
                                    remove_match=[
                                        OIDCProxyHeaderMatch(
                                            name_exact="name_exact_example",
                                            value_regex="value_regex_example",
                                        ),
                                    ],
                                    filters=[
                                        OIDCProxyHeaderRewriteFilter(
                                            rewrite_type="rewrite_type_example",
                                        ),
                                    ],
                                    replace=[
                                        OIDCProxyHeaderReplace(
                                            old_name="old_name_example",
                                            new_name="new_name_example",
                                        ),
                                    ],
                                ),
                            ),
                        ),
                        domain_mapping=OIDCProxyDomainMapping(
                            primary_external_name="app-1.cloud.egov.city",
                            primary_internal_name="app-1.internal",
                            use_service_hostname=True,
                            use_recursive_replacement_system=False,
                            other_mappings=[
                                OIDCProxyDomainNameMapping(
                                    internal_name="local_test_app",
                                    external_name="app-1",
                                ),
                            ],
                        ),
                        auth=OIDCAuthConfig(
                            auth_enabled=True,
                            client_id="admin-portal",
                            issuer="https://auth.cloud.egov.city",
                            logout_url="/login/logout.cfm",
                            scopes=[
                                OIDCProxyScope(
                                    name="urn:agilicus:app:app-1:owner",
                                ),
                            ],
                            path_config=OIDCAuthPathConfig(
                                included_paths=[
                                    OIDCAuthURI(
                                        path="/logout",
                                    ),
                                ],
                                excluded_paths=[
                                    OIDCAuthURI(
                                        path="/logout",
                                    ),
                                ],
                            ),
                            redirect_after_signin_path="/somepath/index.html",
                            redirect_subpath="/somepath/foo",
                        ),
                        content_manipulation=OIDCProxyContentManipulation(
                            media_types=[
                                OIDCContentType(
                                    name="text/css",
                                ),
                            ],
                        ),
                        upstream_config=OIDCProxyUpstreamConfig(
                            scheme="https",
                            hostname="httpbin.org",
                            port=1,
                        ),
                    ),
                    security=ApplicationSecurity(
                        http=HTTPSecuritySettings(
                            csp=CSPSettings(
                                enabled=True,
                                mode="enforce",
                                directives=[
                                    CSPDirective(
                                        name="default-src",
                                        values=[
                                            "https:",
                                        ],
                                    ),
                                ],
                            ),
                            cors=CORSSettings(
                                enabled=True,
                                mode="overwrite",
                                origin_matching="me",
                                allow_resource_origins=True,
                                allow_origins=[
                                    CORSOrigin(
                                        exact="https://other-site.agilicus.cloud",
                                    ),
                                ],
                                allow_methods=[
                                    "POST",
                                ],
                                allow_headers=[
                                    "Destination",
                                ],
                                expose_headers=[
                                    "Location",
                                ],
                                max_age_seconds=3600,
                                allow_credentials=True,
                            ),
                            hsts=HSTSSettings(
                                enabled=True,
                                max_age_seconds=63072000,
                                include_sub_domains=False,
                                preload=True,
                            ),
                            xss_protection=XSSSettings(
                                enabled=True,
                                mode="block",
                                report_uri="https://my-site.agilicus.cloud/xss-reports",
                            ),
                            certificate_transparency=CertificateTransparencySettings(
                                enabled=True,
                                report_uri="https://my-site.agilicus.cloud/ct-reports",
                                enforce=True,
                                max_age_seconds=63072000,
                            ),
                            frame_options=FrameOptionsSettings(
                                enabled=True,
                                mode="deny",
                                override="ALLOW-FROM https://my-site.agilicus.cloud/",
                            ),
                            content_type_options=ContentTypeOptionsSettings(
                                enabled=True,
                                mode="nosniff",
                                override="SomeCustomSetting",
                            ),
                            permitted_cross_domain_policies=PermittedCrossDomainPoliciesSettings(
                                enabled=True,
                                mode="clear",
                                override="master-only",
                            ),
                            coep=CrossOriginEmbedderPolicySettings(
                                enabled=True,
                                mode="unsafe_none",
                                override="some-custom-setting",
                            ),
                            coop=CrossOriginOpenerPolicySettings(
                                enabled=True,
                                mode="unsafe_none",
                                override="some-custom-setting",
                            ),
                            corp=CrossOriginResourcePolicySettings(
                                enabled=True,
                                mode="same_site",
                                override="some-custom-setting",
                            ),
                            referrer_policy=ReferrerPolicySettings(
                                enabled=True,
                                mode="no_referrer",
                                override="some-custom-setting",
                            ),
                        ),
                    ),
                    additional_context=ApplicationAdditionalContext(
                        include_user_context_headers=False,
                    ),
                ),
                name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
                migrated_app_id="migrated_app_id_example",
                proxy_location="in_cloud",
            ),
        ],
        org_id="org_id_example",
        contact_email="contact_email_example",
        monitoring_config=ApplicationMonitoringConfig(
            port=1,
            path="/metrics",
        ),
        port=1,
        healthcheck_uri="healthcheck_uri_example",
        roles=RoleList([
            Role(
                name="name_example",
                rules=[
                    Rule(
                        host="host_example",
                        name="rules.add",
                        method="get",
                        path="/.*",
                        query_parameters=[
                            RuleQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                                match_type="match_type_example",
                            ),
                        ],
                        body=RuleQueryBody(
                            json=[
                                RuleQueryBodyJSON(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]),
        roles_config=RolesConfig(
            roles=[
                RoleConfig(
                    role_name="owner",
                    default=False,
                    description="Provides full access to the the file share.",
                    included_roles=[
                        "included_roles_example",
                    ],
                ),
            ],
        ),
        rules_config=RulesConfig(
            rules=[
                RuleConfig(
                    name="-",
                    roles=[
                        "roles_example",
                    ],
                    excluded_roles=[
                        "excluded_roles_example",
                    ],
                    comments="This rule allows access to all static content of the application for any user, even if they are not authenticated.",
                    condition=HttpRule(
                        rule_type="rule_type_example",
                        condition_type="http_rule_condition",
                        methods=["get"],
                        path_regex="/.*",
                        path_template=TemplatePath(
                            template="/collection/{guid}/subcollection/{sub_guid}",
                            prefix=False,
                        ),
                        query_parameters=[
                            RuleQueryParameter(
                                name="name_example",
                                exact_match="exact_match_example",
                                match_type="match_type_example",
                            ),
                        ],
                        body=RuleQueryBody(
                            json=[
                                RuleQueryBodyJSON(
                                    name="name_example",
                                    exact_match="exact_match_example",
                                    match_type="string",
                                    pointer="/foo/0/a~1b/2",
                                ),
                            ],
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
                    scope=RuleScopeEnum("anyone"),
                    extended_condition=RuleCondition(
                        negated=False,
                        condition=RuleConditionBase(
                            condition_type="CompoundRuleCondition",
                            condition_list=[
                                RuleCondition(),
                            ],
                            list_type="cnf",
                        ),
                    ),
                    priority=1,
                    actions=[
                        RuleAction(
                            action="allow",
                            log_message="rule-1-hit",
                            path="/subpath",
                        ),
                    ],
                ),
            ],
            rule_set_components=[
                RuleSetComponent(
                    parent_rule_name="-",
                    child_rule_name="-",
                    priority=1,
                ),
            ],
        ),
        definitions=[
            Definition(
                key="key_example",
                value="value_example",
            ),
        ],
        assignments=[
            ApplicationAssignment(
                org_id="asd901laskbh",
                environment_name="production",
            ),
        ],
        owned=True,
        maintained=True,
        assigned=True,
        published="no",
        default_role_id="AcaSL40fs22l4Dr4XoAd5y",
        icon_url="icon_url_example",
        display_info=DisplayInfo(
            icons=[
                Icon(
                    uri="https://storage.googleapis.com/agilicus/logo.svg",
                    purposes=[
                        IconPurpose("agilicus-launcher"),
                    ],
                    dimensions=IconDimensions(
                        width=32,
                        height=32,
                    ),
                ),
            ],
            hide="no",
        ),
        location="hosted",
        service_account_required=True,
        application_type="user_defined",
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        workload_config=WorkloadConfiguration(
            env_config_vars=[
                EnvironmentConfigVar(
                    name="_ab2a",
                    value="value_example",
                ),
            ],
        ),
        admin_state=ApplicationStateSelector("active"),
        alternate_mode_setting=AlternateModeSetting(
            learning_mode=LearningModeSpec(
                expiry_time=dateutil_parser('2019-05-16T19:11:18Z'),
            ),
            diagnostic_mode=True,
        ),
        launchers=[
            "123",
        ],
    ) # Application |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Create or update an application
        api_response = api_instance.replace_application(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_application: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Create or update an application
        api_response = api_instance.replace_application(app_id, application=application)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_application: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **application** | [**Application**](Application.md)|  | [optional]

### Return type

[**Application**](Application.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Application was updated. Returns the latest version of it after applying the update.  |  -  |
**404** | Application does not exists |  -  |
**409** | The provided Application conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_config**
> EnvironmentConfig replace_config(app_id, env_name, env_config_id, environment_config)

Update environment configuration

Update environment configuration 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.environment_config import EnvironmentConfig
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    env_config_id = "G" # str | environment configuration id
    environment_config = EnvironmentConfig(
        maintenance_org_id="maintenance_org_id_example",
        config_type="configmap_mount",
        mount_domain="mount_domain_example",
        mount_username="mount_username_example",
        mount_password="mount_password_example",
        mount_hostname="mount.example.com",
        mount_share="mount_share_example",
        mount_src_path="mount_src_path_example",
        mount_path="mount_path_example",
        file_store_uri="file_store_uri_example",
        env_config_vars=[
            EnvironmentConfigVar(
                name="_ab2a",
                value="value_example",
            ),
        ],
    ) # EnvironmentConfig | 

    # example passing only required values which don't have defaults set
    try:
        # Update environment configuration
        api_response = api_instance.replace_config(app_id, env_name, env_config_id, environment_config)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_config: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **env_config_id** | **str**| environment configuration id |
 **environment_config** | [**EnvironmentConfig**](EnvironmentConfig.md)|  |

### Return type

[**EnvironmentConfig**](EnvironmentConfig.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Environment configuration was successfully updated |  -  |
**403** | Reading this environment is not permitted. This could happen due to insufficient permissions within your organisation.  |  -  |
**404** | The Environment configuration does not exist. |  -  |
**409** | The provided Environment Configuration conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_environment**
> Environment replace_environment(app_id, env_name)

Update an environment

This allows an environment maintainer to update the environment. Note that the maintenence_organisation in the body must match the existing one. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.environment import Environment
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    get_scopes = False # bool | In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. (optional) if omitted the server will use the default value of False
    environment = Environment(
        name="name_example",
        maintenance_org_id="maintenance_org_id_example",
        domain_aliases=[
            "uzyBAw2ZuufUOHOEhA8IcFQXnuaZcdyyv0.0.Gpul80FcVjSkp5k.L.Dw-v0dZfUofvKERjsmInY9s-EmMH6kw8gsnXv2Z7jRPK5L.A.q.W.M8pb-ziKqEde8fXg9wdpfxa2-zRi2iAxU4NCUavTrirUe4ba7JnjrgEdBCJZ.w.C.t.g-Vnrj9RmauFxv71lRsCE.Y.V.FKGSDRGKUIQh.KhXoEdbZpGptfI4pvLXGuLk-kwwO2jcMEEkIauW5ApNaDi5ackLaR2kw9-zmvqRnM-dar09VaHCQz0TlT4b42Jml4PJXMF.z8G0e5q9Z4WMWovY63Gk6ixTd5NxRU25mQYd6VBLRGkQ5H9-FH2v5iUaMQ6iIJ-7auxDSR-lIz.7w9bP3XhsKpT6YkX2ymMVYtYsFBx8OyxaBZ75cAidDZ6lvrLQxekRdyiJFjhCbEZunVXTqV3VP-DPO.H.i.VhY.t49MeAEDz67NG9dihNlL1YPO1GvRUDnbsR0-SswaNzc7s9ONPZw-HNPtVfykpnotMPK4Aqhv7VjToBNn1oLr",
        ],
        version_tag="version_tag_example",
        config_mount_path="config_mount_path_example",
        config_as_mount="config_as_mount_example",
        config_as_env="config_as_env_example",
        secrets_mount_path="secrets_mount_path_example",
        secrets_as_mount="secrets_as_mount_example",
        secrets_as_env="secrets_as_env_example",
        serverless_image="serverless_image_example",
        status=EnvironmentStatus(
            runtime_status=RuntimeStatus(
                overall_status="good",
                running_replicas=2,
                error_message="CrashLoopBackoff",
                restarts=5,
                cpu=0.6,
                memory=45.2,
                last_apply_time=dateutil_parser('2002-10-02T10:00:00-05:00'),
                running_image="cr.agilicus.com/applications/iomad:v1.13.0",
                running_hash="sha256:2fb759c1adfe40863b89a4076111af8f210e7342d2240f09b08fc445b357112e",
                org_id="123",
            ),
        ),
        application_configs=ApplicationConfig(
            authentication_config=ApplicationAuthenticationConfig(
                application_handles_authentication=False,
                session_secret="Gns5ZPCvXGjzrtB672HAxfoSQ0dmqriSgiQf6uEQSBU=",
                upstream=OIDCProxyUpstreamAuthentication(
                    ntlm=OIDCProxyUpstreamNTLM(
                        ntlm_passthrough=False,
                    ),
                ),
            ),
            oidc_config=OIDCProxyConfig(
                headers=OIDCProxyHeader(
                    domain_substitution=OIDCProxyDomainSubstitution(
                        standard_headers=OIDCProxyStandardHeader(
                            location=True,
                            origin=True,
                            host=True,
                            set_cookie_header=True,
                            cookie=True,
                        ),
                        other_headers=[
                            OIDCProxyHeaderMapping(
                                name="Accept-Encoding",
                                value="*",
                            ),
                        ],
                        path=True,
                    ),
                    header_overrides=OIDCProxyHeaderOverride(
                        request=OIDCProxyHeaderUserConfig(
                            set=[
                                OIDCProxyHeaderMapping(
                                    name="Accept-Encoding",
                                    value="*",
                                ),
                            ],
                            add=[
                                OIDCProxyHeaderMapping(
                                    name="Accept-Encoding",
                                    value="*",
                                ),
                            ],
                            remove=[
                                OIDCProxyHeaderName(
                                    name="name_example",
                                ),
                            ],
                            remove_match=[
                                OIDCProxyHeaderMatch(
                                    name_exact="name_exact_example",
                                    value_regex="value_regex_example",
                                ),
                            ],
                            filters=[
                                OIDCProxyHeaderRewriteFilter(
                                    rewrite_type="rewrite_type_example",
                                ),
                            ],
                            replace=[
                                OIDCProxyHeaderReplace(
                                    old_name="old_name_example",
                                    new_name="new_name_example",
                                ),
                            ],
                        ),
                        response=OIDCProxyHeaderUserConfig(
                            set=[
                                OIDCProxyHeaderMapping(
                                    name="Accept-Encoding",
                                    value="*",
                                ),
                            ],
                            add=[
                                OIDCProxyHeaderMapping(
                                    name="Accept-Encoding",
                                    value="*",
                                ),
                            ],
                            remove=[
                                OIDCProxyHeaderName(
                                    name="name_example",
                                ),
                            ],
                            remove_match=[
                                OIDCProxyHeaderMatch(
                                    name_exact="name_exact_example",
                                    value_regex="value_regex_example",
                                ),
                            ],
                            filters=[
                                OIDCProxyHeaderRewriteFilter(
                                    rewrite_type="rewrite_type_example",
                                ),
                            ],
                            replace=[
                                OIDCProxyHeaderReplace(
                                    old_name="old_name_example",
                                    new_name="new_name_example",
                                ),
                            ],
                        ),
                    ),
                ),
                domain_mapping=OIDCProxyDomainMapping(
                    primary_external_name="app-1.cloud.egov.city",
                    primary_internal_name="app-1.internal",
                    use_service_hostname=True,
                    use_recursive_replacement_system=False,
                    other_mappings=[
                        OIDCProxyDomainNameMapping(
                            internal_name="local_test_app",
                            external_name="app-1",
                        ),
                    ],
                ),
                auth=OIDCAuthConfig(
                    auth_enabled=True,
                    client_id="admin-portal",
                    issuer="https://auth.cloud.egov.city",
                    logout_url="/login/logout.cfm",
                    scopes=[
                        OIDCProxyScope(
                            name="urn:agilicus:app:app-1:owner",
                        ),
                    ],
                    path_config=OIDCAuthPathConfig(
                        included_paths=[
                            OIDCAuthURI(
                                path="/logout",
                            ),
                        ],
                        excluded_paths=[
                            OIDCAuthURI(
                                path="/logout",
                            ),
                        ],
                    ),
                    redirect_after_signin_path="/somepath/index.html",
                    redirect_subpath="/somepath/foo",
                ),
                content_manipulation=OIDCProxyContentManipulation(
                    media_types=[
                        OIDCContentType(
                            name="text/css",
                        ),
                    ],
                ),
                upstream_config=OIDCProxyUpstreamConfig(
                    scheme="https",
                    hostname="httpbin.org",
                    port=1,
                ),
            ),
            security=ApplicationSecurity(
                http=HTTPSecuritySettings(
                    csp=CSPSettings(
                        enabled=True,
                        mode="enforce",
                        directives=[
                            CSPDirective(
                                name="default-src",
                                values=[
                                    "https:",
                                ],
                            ),
                        ],
                    ),
                    cors=CORSSettings(
                        enabled=True,
                        mode="overwrite",
                        origin_matching="me",
                        allow_resource_origins=True,
                        allow_origins=[
                            CORSOrigin(
                                exact="https://other-site.agilicus.cloud",
                            ),
                        ],
                        allow_methods=[
                            "POST",
                        ],
                        allow_headers=[
                            "Destination",
                        ],
                        expose_headers=[
                            "Location",
                        ],
                        max_age_seconds=3600,
                        allow_credentials=True,
                    ),
                    hsts=HSTSSettings(
                        enabled=True,
                        max_age_seconds=63072000,
                        include_sub_domains=False,
                        preload=True,
                    ),
                    xss_protection=XSSSettings(
                        enabled=True,
                        mode="block",
                        report_uri="https://my-site.agilicus.cloud/xss-reports",
                    ),
                    certificate_transparency=CertificateTransparencySettings(
                        enabled=True,
                        report_uri="https://my-site.agilicus.cloud/ct-reports",
                        enforce=True,
                        max_age_seconds=63072000,
                    ),
                    frame_options=FrameOptionsSettings(
                        enabled=True,
                        mode="deny",
                        override="ALLOW-FROM https://my-site.agilicus.cloud/",
                    ),
                    content_type_options=ContentTypeOptionsSettings(
                        enabled=True,
                        mode="nosniff",
                        override="SomeCustomSetting",
                    ),
                    permitted_cross_domain_policies=PermittedCrossDomainPoliciesSettings(
                        enabled=True,
                        mode="clear",
                        override="master-only",
                    ),
                    coep=CrossOriginEmbedderPolicySettings(
                        enabled=True,
                        mode="unsafe_none",
                        override="some-custom-setting",
                    ),
                    coop=CrossOriginOpenerPolicySettings(
                        enabled=True,
                        mode="unsafe_none",
                        override="some-custom-setting",
                    ),
                    corp=CrossOriginResourcePolicySettings(
                        enabled=True,
                        mode="same_site",
                        override="some-custom-setting",
                    ),
                    referrer_policy=ReferrerPolicySettings(
                        enabled=True,
                        mode="no_referrer",
                        override="some-custom-setting",
                    ),
                ),
            ),
            additional_context=ApplicationAdditionalContext(
                include_user_context_headers=False,
            ),
        ),
        name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
        migrated_app_id="migrated_app_id_example",
        proxy_location="in_cloud",
    ) # Environment |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update an environment
        api_response = api_instance.replace_environment(app_id, env_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_environment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update an environment
        api_response = api_instance.replace_environment(app_id, env_name, get_scopes=get_scopes, environment=environment)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_environment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **get_scopes** | **bool**| In an application or environment GET response, will render all scopes pertaining to an application/environment. For example, rendering will iterate through launchers bound to the application and return all associated application_services as scopes. The returned scopes will also return any scopes provided by the environments application_config. | [optional] if omitted the server will use the default value of False
 **environment** | [**Environment**](Environment.md)|  | [optional]

### Return type

[**Environment**](Environment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Environment was updated. Returns the latest version of it after the update was applied.  |  -  |
**403** | Modifying this environment is not permitted. This could happen due to insufficient permissions within your organisation, or because you tried to change the maintenence organisation of an environment.  |  -  |
**404** | The Environment does not exist. |  -  |
**409** | The provided Environment conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_role**
> RoleV2 replace_role(app_id, role_id)

Update a role

Updates a role with a new specification. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.role_v2 import RoleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_id = "Absadal2" # str | The id of a role
    role_v2 = RoleV2(
        metadata=MetadataWithId(),
        spec=RoleSpec(
            app_id="123",
            name="owner",
            comments="This role allows access to all read-only endpoints of the application. Assign this role to anybody who needs to be able to interact with the application in a read-only fashion, such as an auditor.",
            included=[
                IncludedRole(
                    role_id="123",
                ),
            ],
            org_id="123",
        ),
    ) # RoleV2 |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a role
        api_response = api_instance.replace_role(app_id, role_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_role: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a role
        api_response = api_instance.replace_role(app_id, role_id, role_v2=role_v2)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_id** | **str**| The id of a role |
 **role_v2** | [**RoleV2**](RoleV2.md)|  | [optional]

### Return type

[**RoleV2**](RoleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Role was updated. Returns the latest version of it after the update was applied.  |  -  |
**404** | The Role does not exist. |  -  |
**409** | The provided Role conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_role_to_rule_entry**
> RoleToRuleEntry replace_role_to_rule_entry(app_id, role_to_rule_entry_id)

Update a role_to_rule_entry

Updates a role_to_rule_entry with a new specification. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.role_to_rule_entry import RoleToRuleEntry
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    role_to_rule_entry_id = "Absadal2" # str | The id of a role to rule entry
    role_to_rule_entry = RoleToRuleEntry(
        metadata=MetadataWithId(),
        spec=RoleToRuleEntrySpec(
            role_id="123",
            rule_id="123",
            app_id="123",
            org_id="123",
            included=True,
        ),
    ) # RoleToRuleEntry |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a role_to_rule_entry
        api_response = api_instance.replace_role_to_rule_entry(app_id, role_to_rule_entry_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_role_to_rule_entry: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a role_to_rule_entry
        api_response = api_instance.replace_role_to_rule_entry(app_id, role_to_rule_entry_id, role_to_rule_entry=role_to_rule_entry)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_role_to_rule_entry: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **role_to_rule_entry_id** | **str**| The id of a role to rule entry |
 **role_to_rule_entry** | [**RoleToRuleEntry**](RoleToRuleEntry.md)|  | [optional]

### Return type

[**RoleToRuleEntry**](RoleToRuleEntry.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The RoleToRuleEntry was updated. Returns the latest version of it after the update was applied.  |  -  |
**404** | The RoleToRuleEntry does not exist. |  -  |
**409** | The provided RoleToRuleEntry conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_rule**
> RuleV2 replace_rule(app_id, rule_id)

Update a rule

Updates a rule with a new specification. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.rule_v2 import RuleV2
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    rule_id = "Absadal2" # str | The id of a rule
    rule_v2 = RuleV2(
        metadata=MetadataWithId(),
        spec=RuleSpec(
            app_id="123",
            comments="This rule allows access to all static content of the application for any user, even if they are not authenticated.",
            condition=HttpRule(
                rule_type="rule_type_example",
                condition_type="http_rule_condition",
                methods=["get"],
                path_regex="/.*",
                path_template=TemplatePath(
                    template="/collection/{guid}/subcollection/{sub_guid}",
                    prefix=False,
                ),
                query_parameters=[
                    RuleQueryParameter(
                        name="name_example",
                        exact_match="exact_match_example",
                        match_type="match_type_example",
                    ),
                ],
                body=RuleQueryBody(
                    json=[
                        RuleQueryBodyJSON(
                            name="name_example",
                            exact_match="exact_match_example",
                            match_type="string",
                            pointer="/foo/0/a~1b/2",
                        ),
                    ],
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
            org_id="123",
            scope=RuleScopeEnum("anyone"),
        ),
    ) # RuleV2 |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a rule
        api_response = api_instance.replace_rule(app_id, rule_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a rule
        api_response = api_instance.replace_rule(app_id, rule_id, rule_v2=rule_v2)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **rule_id** | **str**| The id of a rule |
 **rule_v2** | [**RuleV2**](RuleV2.md)|  | [optional]

### Return type

[**RuleV2**](RuleV2.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Rule was updated. Returns the latest version of it after the update was applied.  |  -  |
**404** | The Rule does not exist. |  -  |
**409** | The provided Rule conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_runtime_status**
> RuntimeStatus replace_runtime_status(app_id, env_name, runtime_status)

update an environemnt's runtime status

update an environemnt's runtime status

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.runtime_status import RuntimeStatus
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    env_name = "G" # str | The name of an Environment
    runtime_status = RuntimeStatus(
        overall_status="good",
        running_replicas=2,
        error_message="CrashLoopBackoff",
        restarts=5,
        cpu=0.6,
        memory=45.2,
        last_apply_time=dateutil_parser('2002-10-02T10:00:00-05:00'),
        running_image="cr.agilicus.com/applications/iomad:v1.13.0",
        running_hash="sha256:2fb759c1adfe40863b89a4076111af8f210e7342d2240f09b08fc445b357112e",
        org_id="123",
    ) # RuntimeStatus | 

    # example passing only required values which don't have defaults set
    try:
        # update an environemnt's runtime status
        api_response = api_instance.replace_runtime_status(app_id, env_name, runtime_status)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->replace_runtime_status: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **env_name** | **str**| The name of an Environment |
 **runtime_status** | [**RuntimeStatus**](RuntimeStatus.md)|  |

### Return type

[**RuntimeStatus**](RuntimeStatus.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Update the environment&#39;s runtime status |  -  |
**403** | Changing the environment status is not permitted.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_patch_application**
> Application update_patch_application(app_id)

patch application

patch application

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import applications_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.org_scope_patch_document import OrgScopePatchDocument
from agilicus_api.model.application import Application
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
    api_instance = applications_api.ApplicationsApi(api_client)
    app_id = "G" # str | Application unique identifier
    org_scope_patch_document = OrgScopePatchDocument(
        org_id="org_id_example",
        patches=[
            {},
        ],
    ) # OrgScopePatchDocument |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # patch application
        api_response = api_instance.update_patch_application(app_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->update_patch_application: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # patch application
        api_response = api_instance.update_patch_application(app_id, org_scope_patch_document=org_scope_patch_document)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ApplicationsApi->update_patch_application: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| Application unique identifier |
 **org_scope_patch_document** | [**OrgScopePatchDocument**](OrgScopePatchDocument.md)|  | [optional]

### Return type

[**Application**](Application.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Patch application  |  -  |
**404** | Application or JSON PATH does not exists |  -  |
**409** | The provided PatchDocument conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

