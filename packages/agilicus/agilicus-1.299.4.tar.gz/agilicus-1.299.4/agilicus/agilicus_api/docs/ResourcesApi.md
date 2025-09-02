# agilicus_api.ResourcesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_resource**](ResourcesApi.md#add_resource) | **POST** /v1/resources | Add a resource
[**delete_resource**](ResourcesApi.md#delete_resource) | **DELETE** /v1/resources/{resource_id} | Delete a resource
[**get_resource**](ResourcesApi.md#get_resource) | **GET** /v1/resources/{resource_id} | Get a resource
[**list_combined_resource_rules**](ResourcesApi.md#list_combined_resource_rules) | **GET** /v1/combined_resource_rules | List rules combined by scope or role
[**list_resource_groups**](ResourcesApi.md#list_resource_groups) | **GET** /v1/resources/groups | List resource groups and their children.
[**list_resource_guid_mapping**](ResourcesApi.md#list_resource_guid_mapping) | **GET** /v1/resources/guids | Get all resource guids and a unique name mapping
[**list_resources**](ResourcesApi.md#list_resources) | **GET** /v1/resources | List all Resources
[**reconcile_default_policy**](ResourcesApi.md#reconcile_default_policy) | **POST** /v1/resources/{resource_id}/reconcile_default_policy | Reconciles the default policy for a resource
[**replace_resource**](ResourcesApi.md#replace_resource) | **PUT** /v1/resources/{resource_id} | update a resource


# **add_resource**
> Resource add_resource(resource)

Add a resource

Add a new resource of a specific type. This API is used specifically for resource_type=group, where there is no derived type resource for this object. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.resource import Resource
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
    api_instance = resources_api.ResourcesApi(api_client)
    resource = Resource(
        metadata=MetadataWithId(),
        spec=ResourceSpec(
            name="my-application",
            resource_type=ResourceTypeEnum("application"),
            org_id="S38d8dk3Xirt69",
            name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
            not_assignable_perm=True,
            config=ResourceConfig(
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
                published="no",
            ),
            resource_members=[
                ResourceMember(
                    id="123",
                    resource_type=ResourceTypeEnum("application"),
                ),
            ],
            bundle_id="123",
            demo=False,
        ),
        status=ResourceStatus(
            resource_stats=ResourceStats(
                resource_id="S38d8dk3Xirt69",
                metadata=ResourceStatsMetadata(
                    collection_time=dateutil_parser('2020-07-07T15:49:51.23Z'),
                ),
                overall_status="overall_status_example",
                last_warning_message="last_warning_message_example",
                session_stats=ResourceSessionStats(
                    total=1,
                    allowed=1,
                    denied=1,
                    failed=1,
                ),
            ),
            all_roles=[
                RoleConfig(
                    role_name="owner",
                    default=False,
                    description="Provides full access to the the file share.",
                    included_roles=[
                        "included_roles_example",
                    ],
                ),
            ],
            resource_members=[
                Resource(),
            ],
            resource_urls=[
                ResourceURL(
                    url="https://a-resource.acme-customer.agilicus.cloud",
                ),
            ],
            ruleset_label="123",
        ),
    ) # Resource | 

    # example passing only required values which don't have defaults set
    try:
        # Add a resource
        api_response = api_instance.add_resource(resource)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->add_resource: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | [**Resource**](Resource.md)|  |

### Return type

[**Resource**](Resource.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New resource created |  -  |
**409** | Resource already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource**
> delete_resource(resource_id)

Delete a resource

Delete a resource

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
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
    api_instance = resources_api.ResourcesApi(api_client)
    resource_id = "X1Isks5kslds945" # str | The id of the resource to access
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a resource
        api_instance.delete_resource(resource_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->delete_resource: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a resource
        api_instance.delete_resource(resource_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->delete_resource: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_id** | **str**| The id of the resource to access |
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
**204** | Resource was deleted |  -  |
**404** | Resource does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource**
> Resource get_resource(resource_id)

Get a resource

Get a resource

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.resource import Resource
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
    api_instance = resources_api.ResourcesApi(api_client)
    resource_id = "X1Isks5kslds945" # str | The id of the resource to access
    org_id = "1234" # str | Organisation Unique identifier (optional)
    expand_resource_members = False # bool | On resource requests, when True will populate member_resources with its full Resource object.  (optional) if omitted the server will use the default value of False
    include_legacy_icon_info = False # bool | Instructs resources to fetch legacy (e.g. non-ResourceConfig) icon info.  (optional) if omitted the server will use the default value of False
    resource_urls = True # bool | Retrieve associated resource urls in request.  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a resource
        api_response = api_instance.get_resource(resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->get_resource: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a resource
        api_response = api_instance.get_resource(resource_id, org_id=org_id, expand_resource_members=expand_resource_members, include_legacy_icon_info=include_legacy_icon_info, resource_urls=resource_urls)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->get_resource: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_id** | **str**| The id of the resource to access |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **expand_resource_members** | **bool**| On resource requests, when True will populate member_resources with its full Resource object.  | [optional] if omitted the server will use the default value of False
 **include_legacy_icon_info** | **bool**| Instructs resources to fetch legacy (e.g. non-ResourceConfig) icon info.  | [optional] if omitted the server will use the default value of False
 **resource_urls** | **bool**| Retrieve associated resource urls in request.  | [optional]

### Return type

[**Resource**](Resource.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a Resource |  -  |
**404** | Resource does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_combined_resource_rules**
> ListCombinedResourceRulesResponse list_combined_resource_rules()

List rules combined by scope or role

Retrieve all role_to_rule_entries for resources. If assigned is true, this will list all role_to_rule_entries for applications assigned to the given org_id 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.rule_scope_enum import RuleScopeEnum
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.list_combined_resource_rules_response import ListCombinedResourceRulesResponse
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
    api_instance = resources_api.ResourcesApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    scopes = [
        RuleScopeEnum("["anyone"]"),
    ] # [RuleScopeEnum] | The scopes of the rules to search for. Multiple values are ORed together. (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    assigned = True # bool | Query for Applications assigned to the `org_id`. These are Applications with at least one Environment assigned to the `org_id`.  (optional)
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List rules combined by scope or role
        api_response = api_instance.list_combined_resource_rules(org_id=org_id, scopes=scopes, resource_id=resource_id, limit=limit, assigned=assigned, resource_type=resource_type)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->list_combined_resource_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **scopes** | [**[RuleScopeEnum]**](RuleScopeEnum.md)| The scopes of the rules to search for. Multiple values are ORed together. | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **assigned** | **bool**| Query for Applications assigned to the &#x60;org_id&#x60;. These are Applications with at least one Environment assigned to the &#x60;org_id&#x60;.  | [optional]
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]

### Return type

[**ListCombinedResourceRulesResponse**](ListCombinedResourceRulesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | CombinedResourceRules were successfully retrieved |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_resource_groups**
> ListResourceGroupsResponse list_resource_groups()

List resource groups and their children.

List all resource groups and their children. This is an optimized query that minimizes the returned result to guids only. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.list_resource_groups_response import ListResourceGroupsResponse
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
    api_instance = resources_api.ResourcesApi(api_client)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List resource groups and their children.
        api_response = api_instance.list_resource_groups(org_ids=org_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->list_resource_groups: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]

### Return type

[**ListResourceGroupsResponse**](ListResourceGroupsResponse.md)

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

# **list_resource_guid_mapping**
> ListGuidMetadataResponse list_resource_guid_mapping()

Get all resource guids and a unique name mapping

Get all resource guids and a unique name mapping

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
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
    api_instance = resources_api.ResourcesApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    previous_guid = "73WakrfVbNJBaAmhQtEeDv" # str | Pagination based query with the guid as the key. To get the initial entries supply an empty string. (optional)
    updated_since = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime | query since updated (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all resource guids and a unique name mapping
        api_response = api_instance.list_resource_guid_mapping(org_id=org_id, resource_id=resource_id, limit=limit, previous_guid=previous_guid, updated_since=updated_since)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->list_resource_guid_mapping: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **previous_guid** | **str**| Pagination based query with the guid as the key. To get the initial entries supply an empty string. | [optional]
 **updated_since** | **datetime**| query since updated | [optional]

### Return type

[**ListGuidMetadataResponse**](ListGuidMetadataResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return GuidToName mapping |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_resources**
> ListResourcesResponse list_resources()

List all Resources

List all Resources matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.list_resources_response import ListResourcesResponse
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
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
    api_instance = resources_api.ResourcesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    exclude_resource_type = [
        "fileshare",
    ] # [str] | Resource types to exclude (optional)
    name_slug = "smy-application1234" # str | The slug of the resource to query for (optional)
    name = "my-application" # str | The name of the resource to query for (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)
    expand_resource_members = False # bool | On resource requests, when True will populate member_resources with its full Resource object.  (optional) if omitted the server will use the default value of False
    include_legacy_icon_info = False # bool | Instructs resources to fetch legacy (e.g. non-ResourceConfig) icon info.  (optional) if omitted the server will use the default value of False
    resource_urls = True # bool | Retrieve associated resource urls in request.  (optional)
    show_stats = True # bool | Whether the return value should include the stats for included objects. If false the query may run faster but will not include statistics. If not present, defaults to false.  (optional) if omitted the server will use the default value of False

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all Resources
        api_response = api_instance.list_resources(limit=limit, org_id=org_id, resource_type=resource_type, exclude_resource_type=exclude_resource_type, name_slug=name_slug, name=name, resource_id=resource_id, page_at_id=page_at_id, org_ids=org_ids, expand_resource_members=expand_resource_members, include_legacy_icon_info=include_legacy_icon_info, resource_urls=resource_urls, show_stats=show_stats)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->list_resources: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **exclude_resource_type** | **[str]**| Resource types to exclude | [optional]
 **name_slug** | **str**| The slug of the resource to query for | [optional]
 **name** | **str**| The name of the resource to query for | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]
 **expand_resource_members** | **bool**| On resource requests, when True will populate member_resources with its full Resource object.  | [optional] if omitted the server will use the default value of False
 **include_legacy_icon_info** | **bool**| Instructs resources to fetch legacy (e.g. non-ResourceConfig) icon info.  | [optional] if omitted the server will use the default value of False
 **resource_urls** | **bool**| Retrieve associated resource urls in request.  | [optional]
 **show_stats** | **bool**| Whether the return value should include the stats for included objects. If false the query may run faster but will not include statistics. If not present, defaults to false.  | [optional] if omitted the server will use the default value of False

### Return type

[**ListResourcesResponse**](ListResourcesResponse.md)

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

# **reconcile_default_policy**
> Resource reconcile_default_policy(resource_id)

Reconciles the default policy for a resource

Reconciles the default policy for a resource

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.resource import Resource
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
    api_instance = resources_api.ResourcesApi(api_client)
    resource_id = "X1Isks5kslds945" # str | The id of the resource to access
    resource = Resource(
        metadata=MetadataWithId(),
        spec=ResourceSpec(
            name="my-application",
            resource_type=ResourceTypeEnum("application"),
            org_id="S38d8dk3Xirt69",
            name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
            not_assignable_perm=True,
            config=ResourceConfig(
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
                published="no",
            ),
            resource_members=[
                ResourceMember(
                    id="123",
                    resource_type=ResourceTypeEnum("application"),
                ),
            ],
            bundle_id="123",
            demo=False,
        ),
        status=ResourceStatus(
            resource_stats=ResourceStats(
                resource_id="S38d8dk3Xirt69",
                metadata=ResourceStatsMetadata(
                    collection_time=dateutil_parser('2020-07-07T15:49:51.23Z'),
                ),
                overall_status="overall_status_example",
                last_warning_message="last_warning_message_example",
                session_stats=ResourceSessionStats(
                    total=1,
                    allowed=1,
                    denied=1,
                    failed=1,
                ),
            ),
            all_roles=[
                RoleConfig(
                    role_name="owner",
                    default=False,
                    description="Provides full access to the the file share.",
                    included_roles=[
                        "included_roles_example",
                    ],
                ),
            ],
            resource_members=[
                Resource(),
            ],
            resource_urls=[
                ResourceURL(
                    url="https://a-resource.acme-customer.agilicus.cloud",
                ),
            ],
            ruleset_label="123",
        ),
    ) # Resource |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Reconciles the default policy for a resource
        api_response = api_instance.reconcile_default_policy(resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->reconcile_default_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Reconciles the default policy for a resource
        api_response = api_instance.reconcile_default_policy(resource_id, resource=resource)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->reconcile_default_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_id** | **str**| The id of the resource to access |
 **resource** | [**Resource**](Resource.md)|  | [optional]

### Return type

[**Resource**](Resource.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ruleset_bundle_id created |  -  |
**404** | Resource does not exist |  -  |
**409** | rulset_bundle_id already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_resource**
> Resource replace_resource(resource_id)

update a resource

update a resource

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import resources_api
from agilicus_api.model.resource import Resource
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
    api_instance = resources_api.ResourcesApi(api_client)
    resource_id = "X1Isks5kslds945" # str | The id of the resource to access
    resource = Resource(
        metadata=MetadataWithId(),
        spec=ResourceSpec(
            name="my-application",
            resource_type=ResourceTypeEnum("application"),
            org_id="S38d8dk3Xirt69",
            name_slug=K8sSlug("81c2v7s6djuy1zmetozkhdomha1bae37b8ocvx8o53ow2eg7p6qw9qklp6l4y010fogx"),
            not_assignable_perm=True,
            config=ResourceConfig(
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
                published="no",
            ),
            resource_members=[
                ResourceMember(
                    id="123",
                    resource_type=ResourceTypeEnum("application"),
                ),
            ],
            bundle_id="123",
            demo=False,
        ),
        status=ResourceStatus(
            resource_stats=ResourceStats(
                resource_id="S38d8dk3Xirt69",
                metadata=ResourceStatsMetadata(
                    collection_time=dateutil_parser('2020-07-07T15:49:51.23Z'),
                ),
                overall_status="overall_status_example",
                last_warning_message="last_warning_message_example",
                session_stats=ResourceSessionStats(
                    total=1,
                    allowed=1,
                    denied=1,
                    failed=1,
                ),
            ),
            all_roles=[
                RoleConfig(
                    role_name="owner",
                    default=False,
                    description="Provides full access to the the file share.",
                    included_roles=[
                        "included_roles_example",
                    ],
                ),
            ],
            resource_members=[
                Resource(),
            ],
            resource_urls=[
                ResourceURL(
                    url="https://a-resource.acme-customer.agilicus.cloud",
                ),
            ],
            ruleset_label="123",
        ),
    ) # Resource |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a resource
        api_response = api_instance.replace_resource(resource_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->replace_resource: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a resource
        api_response = api_instance.replace_resource(resource_id, resource=resource)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ResourcesApi->replace_resource: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_id** | **str**| The id of the resource to access |
 **resource** | [**Resource**](Resource.md)|  | [optional]

### Return type

[**Resource**](Resource.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated Resource |  -  |
**404** | Resource does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

