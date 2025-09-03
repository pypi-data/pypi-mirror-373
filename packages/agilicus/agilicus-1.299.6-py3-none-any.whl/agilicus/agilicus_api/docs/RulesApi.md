# agilicus_api.RulesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cleanup_standalone_rules**](RulesApi.md#cleanup_standalone_rules) | **POST** /v1/standalone_rules/cleanup | cleanup of standalone rules
[**create_ruleset_label**](RulesApi.md#create_ruleset_label) | **POST** /v1/standalone_ruleset_labels | Creates a StandaloneRulesetLabel
[**create_standalone_rule**](RulesApi.md#create_standalone_rule) | **POST** /v1/standalone_rules | Add a standalone rule
[**create_standalone_rule_policy**](RulesApi.md#create_standalone_rule_policy) | **POST** /v1/standalone_rule_policies | Add a standalone rule policy
[**create_standalone_rule_tree**](RulesApi.md#create_standalone_rule_tree) | **POST** /v1/standalone_rule_trees | Add a standalone rule tree
[**create_standalone_ruleset**](RulesApi.md#create_standalone_ruleset) | **POST** /v1/standalone_rulesets | Add a standalone ruleset
[**create_standalone_ruleset_bundle**](RulesApi.md#create_standalone_ruleset_bundle) | **POST** /v1/standalone_ruleset_bundles | Add a standalone ruleset bundle
[**delete_ruleset_label**](RulesApi.md#delete_ruleset_label) | **DELETE** /v1/standalone_ruleset_labels/{label} | Delete a StandaloneRulesetLabel
[**delete_standalone_rule**](RulesApi.md#delete_standalone_rule) | **DELETE** /v1/standalone_rules/{rule_id} | Delete a standalone rule
[**delete_standalone_rule_policy**](RulesApi.md#delete_standalone_rule_policy) | **DELETE** /v1/standalone_rule_policies/{standalone_rule_policy_id} | Delete a standalone rule policy
[**delete_standalone_rule_tree**](RulesApi.md#delete_standalone_rule_tree) | **DELETE** /v1/standalone_rule_trees/{standalone_rule_tree_id} | Delete a standalone rule tree
[**delete_standalone_ruleset**](RulesApi.md#delete_standalone_ruleset) | **DELETE** /v1/standalone_rulesets/{standalone_ruleset_id} | Delete a standalone ruleset
[**delete_standalone_ruleset_bundle**](RulesApi.md#delete_standalone_ruleset_bundle) | **DELETE** /v1/standalone_ruleset_bundles/{standalone_ruleset_bundle_id} | Delete a standalone ruleset_bundle
[**get_ruleset_label**](RulesApi.md#get_ruleset_label) | **GET** /v1/standalone_ruleset_labels/{label} | Get a StandaloneRulesetLabel
[**get_standalone_rule**](RulesApi.md#get_standalone_rule) | **GET** /v1/standalone_rules/{rule_id} | Get a standalone rule
[**get_standalone_rule_policy**](RulesApi.md#get_standalone_rule_policy) | **GET** /v1/standalone_rule_policies/{standalone_rule_policy_id} | Get a standalone rule policy
[**get_standalone_rule_tree**](RulesApi.md#get_standalone_rule_tree) | **GET** /v1/standalone_rule_trees/{standalone_rule_tree_id} | Get a standalone rule tree
[**get_standalone_ruleset**](RulesApi.md#get_standalone_ruleset) | **GET** /v1/standalone_rulesets/{standalone_ruleset_id} | Get a standalone ruleset
[**get_standalone_ruleset_bundle**](RulesApi.md#get_standalone_ruleset_bundle) | **GET** /v1/standalone_ruleset_bundles/{standalone_ruleset_bundle_id} | Get a standalone ruleset bundle
[**list_ruleset_labels**](RulesApi.md#list_ruleset_labels) | **GET** /v1/standalone_ruleset_labels | list StandaloneRulesetLabel
[**list_standalone_rule_policies**](RulesApi.md#list_standalone_rule_policies) | **GET** /v1/standalone_rule_policies | List all standalone rule policies
[**list_standalone_rule_trees**](RulesApi.md#list_standalone_rule_trees) | **GET** /v1/standalone_rule_trees | List all standalone rule trees
[**list_standalone_rules**](RulesApi.md#list_standalone_rules) | **GET** /v1/standalone_rules | List all standalone rules
[**list_standalone_ruleset_bundles**](RulesApi.md#list_standalone_ruleset_bundles) | **GET** /v1/standalone_ruleset_bundles | List all standalone ruleset bundles
[**list_standalone_rulesets**](RulesApi.md#list_standalone_rulesets) | **GET** /v1/standalone_rulesets | List all standalone rulesets
[**replace_standalone_rule**](RulesApi.md#replace_standalone_rule) | **PUT** /v1/standalone_rules/{rule_id} | update a standalone rule
[**replace_standalone_rule_policy**](RulesApi.md#replace_standalone_rule_policy) | **PUT** /v1/standalone_rule_policies/{standalone_rule_policy_id} | update a standalone rule policy
[**replace_standalone_rule_tree**](RulesApi.md#replace_standalone_rule_tree) | **PUT** /v1/standalone_rule_trees/{standalone_rule_tree_id} | update a standalone rule tree
[**replace_standalone_ruleset**](RulesApi.md#replace_standalone_ruleset) | **PUT** /v1/standalone_rulesets/{standalone_ruleset_id} | update a standalone ruleset
[**replace_standalone_ruleset_bundle**](RulesApi.md#replace_standalone_ruleset_bundle) | **PUT** /v1/standalone_ruleset_bundles/{standalone_ruleset_bundle_id} | update a standalone ruleset bundle


# **cleanup_standalone_rules**
> StandaloneRulesCleanup cleanup_standalone_rules()

cleanup of standalone rules

deletion of all standalone rules/sets/labels/bundles that are associated with object_type,object_id and label 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rules_cleanup import StandaloneRulesCleanup
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rules_cleanup = StandaloneRulesCleanup(
        spec=StandaloneRulesCleanupSpec(
            org_id="123",
            object_type=EmptiableObjectType("desktop"),
            object_id="123",
            labels=[
                StandaloneRulesetLabelName("agilicus-defaults"),
            ],
        ),
        status=StandaloneRulesCleanupStatus(
            bundles_deleted=[
                "123",
            ],
            rule_policies_deleted=[
                "123",
            ],
            labels_deleted=[
                StandaloneRulesetLabelName("agilicus-defaults"),
            ],
        ),
    ) # StandaloneRulesCleanup |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # cleanup of standalone rules
        api_response = api_instance.cleanup_standalone_rules(standalone_rules_cleanup=standalone_rules_cleanup)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->cleanup_standalone_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rules_cleanup** | [**StandaloneRulesCleanup**](StandaloneRulesCleanup.md)|  | [optional]

### Return type

[**StandaloneRulesCleanup**](StandaloneRulesCleanup.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | cleanup completed |  -  |
**404** | no rules exist with provided parameters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_ruleset_label**
> StandaloneRulesetLabel create_ruleset_label(standalone_ruleset_label)

Creates a StandaloneRulesetLabel

Creates a StandaloneRulesetLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_ruleset_label import StandaloneRulesetLabel
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_label = StandaloneRulesetLabel(
        metadata=CommonMetadata(
        ),
        spec=StandaloneRulesetLabelSpec(
            name=StandaloneRulesetLabelName("agilicus-defaults"),
            org_id="123",
        ),
        status=StandaloneRulesetLabelStatus(
        ),
    ) # StandaloneRulesetLabel | 

    # example passing only required values which don't have defaults set
    try:
        # Creates a StandaloneRulesetLabel
        api_response = api_instance.create_ruleset_label(standalone_ruleset_label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_ruleset_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_label** | [**StandaloneRulesetLabel**](StandaloneRulesetLabel.md)|  |

### Return type

[**StandaloneRulesetLabel**](StandaloneRulesetLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | StandaloneRulesetLabel created and returned. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_rule**
> StandaloneRule create_standalone_rule(standalone_rule)

Add a standalone rule

Adds a new standalone rule. Rules must have unique names within an org. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule import StandaloneRule
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule = StandaloneRule(
        metadata=MetadataWithId(),
        spec=StandaloneRuleSpec(
            rule=RuleConfig(
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
            org_id="123",
            purpose="ag-revocation-proxy",
            standalone_rule_policy_id="123",
        ),
    ) # StandaloneRule | 

    # example passing only required values which don't have defaults set
    try:
        # Add a standalone rule
        api_response = api_instance.create_standalone_rule(standalone_rule)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_standalone_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule** | [**StandaloneRule**](StandaloneRule.md)|  |

### Return type

[**StandaloneRule**](StandaloneRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New standalone rule created. |  -  |
**400** | The request is invalid |  -  |
**409** | Standalone rule already exists. The existing rule is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_rule_policy**
> StandaloneRulePolicy create_standalone_rule_policy(standalone_rule_policy)

Add a standalone rule policy

Adds a new standalone rule policy. Policies must have a unique (object_type, object_id, policy_class, policy_name) is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule_policy import StandaloneRulePolicy
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_policy = StandaloneRulePolicy(
        metadata=MetadataWithId(),
        spec=StandaloneRulePolicySpec(
            org_id="123",
            object_type=EmptiableObjectType("desktop"),
            object_id="123",
            policy_class="mfa",
            policy_instance="default-mfa-policy",
            description=StandaloneRulePolicyDescription("/"),
            annotations={},
        ),
    ) # StandaloneRulePolicy | 

    # example passing only required values which don't have defaults set
    try:
        # Add a standalone rule policy
        api_response = api_instance.create_standalone_rule_policy(standalone_rule_policy)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_standalone_rule_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_policy** | [**StandaloneRulePolicy**](StandaloneRulePolicy.md)|  |

### Return type

[**StandaloneRulePolicy**](StandaloneRulePolicy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New standalone rule policy created. |  -  |
**400** | The request is invalid |  -  |
**409** | standalone rule policy already exists. The existing standalone rule policy is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_rule_tree**
> StandaloneRuleTree create_standalone_rule_tree(standalone_rule_tree)

Add a standalone rule tree

Adds a new standalone rule tree. Rule trees must have unique names within an org. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_rule_tree import StandaloneRuleTree
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_tree = StandaloneRuleTree(
        metadata=MetadataWithId(),
        spec=StandaloneRuleTreeSpec(
            name=StandaloneRuleName("my-rule"),
            tree=StandaloneRuleTreeNode(
                children=[
                    StandaloneRuleTreeNodeChild(
                        priority=0,
                        node=StandaloneRuleTreeNode(),
                    ),
                ],
                rules=[
                    StandaloneRuleTreeRuleRef(
                        rule_name=StandaloneRuleName("my-rule"),
                    ),
                ],
                require_children_true=True,
            ),
            org_id="123",
            object_conditions=StandaloneObjectConditions(
                scopes=[
                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                ],
            ),
            description="/",
            standalone_rule_policy_id="123",
        ),
        status=StandaloneRuleTreeStatus(
            tree=DereferencedStandaloneRuleTreeNode(
                children=[
                    DereferencedStandaloneRuleTreeNodeChild(
                        priority=0,
                        node=DereferencedStandaloneRuleTreeNode(),
                    ),
                ],
                rules=[
                    StandaloneRule(
                        metadata=MetadataWithId(),
                        spec=StandaloneRuleSpec(
                            rule=RuleConfig(
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
                            org_id="123",
                            purpose="ag-revocation-proxy",
                            standalone_rule_policy_id="123",
                        ),
                    ),
                ],
                object_conditions=StandaloneObjectConditions(
                    scopes=[
                        StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                    ],
                ),
            ),
        ),
    ) # StandaloneRuleTree | 

    # example passing only required values which don't have defaults set
    try:
        # Add a standalone rule tree
        api_response = api_instance.create_standalone_rule_tree(standalone_rule_tree)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_standalone_rule_tree: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_tree** | [**StandaloneRuleTree**](StandaloneRuleTree.md)|  |

### Return type

[**StandaloneRuleTree**](StandaloneRuleTree.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New standalone rule tree created. |  -  |
**400** | The request is invalid |  -  |
**409** | standalone rule tree already exists. The existing rule tree is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_ruleset**
> StandaloneRuleset create_standalone_ruleset(standalone_ruleset)

Add a standalone ruleset

Adds a new standalone ruleset. rulesets must have unique names within an org. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_ruleset import StandaloneRuleset
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset = StandaloneRuleset(
        metadata=MetadataWithId(),
        spec=StandaloneRulesetSpec(
            name=StandaloneRuleName("my-rule"),
            labels=[
                StandaloneRulesetLabelName("agilicus-defaults"),
            ],
            org_id="123",
            object_conditions=StandaloneObjectConditions(
                scopes=[
                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                ],
            ),
            rule_trees=[
                StandaloneRuleTreeRef(
                    rule_tree_name=StandaloneRuleName("my-rule"),
                    priority=0,
                ),
            ],
            standalone_rule_policy_id="123",
        ),
        status=StandaloneRulesetStatus(
            rule_trees=[
                StandaloneRuleTree(
                    metadata=MetadataWithId(),
                    spec=StandaloneRuleTreeSpec(
                        name=StandaloneRuleName("my-rule"),
                        tree=StandaloneRuleTreeNode(
                            children=[
                                StandaloneRuleTreeNodeChild(
                                    priority=0,
                                    node=StandaloneRuleTreeNode(),
                                ),
                            ],
                            rules=[
                                StandaloneRuleTreeRuleRef(
                                    rule_name=StandaloneRuleName("my-rule"),
                                ),
                            ],
                            require_children_true=True,
                        ),
                        org_id="123",
                        object_conditions=StandaloneObjectConditions(
                            scopes=[
                                StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                            ],
                        ),
                        description="/",
                        standalone_rule_policy_id="123",
                    ),
                    status=StandaloneRuleTreeStatus(
                        tree=DereferencedStandaloneRuleTreeNode(
                            children=[
                                DereferencedStandaloneRuleTreeNodeChild(
                                    priority=0,
                                    node=DereferencedStandaloneRuleTreeNode(),
                                ),
                            ],
                            rules=[
                                StandaloneRule(
                                    metadata=MetadataWithId(),
                                    spec=StandaloneRuleSpec(
                                        rule=RuleConfig(
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
                                        org_id="123",
                                        purpose="ag-revocation-proxy",
                                        standalone_rule_policy_id="123",
                                    ),
                                ),
                            ],
                            object_conditions=StandaloneObjectConditions(
                                scopes=[
                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                ],
                            ),
                        ),
                    ),
                ),
            ],
        ),
    ) # StandaloneRuleset | 

    # example passing only required values which don't have defaults set
    try:
        # Add a standalone ruleset
        api_response = api_instance.create_standalone_ruleset(standalone_ruleset)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_standalone_ruleset: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset** | [**StandaloneRuleset**](StandaloneRuleset.md)|  |

### Return type

[**StandaloneRuleset**](StandaloneRuleset.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New standalone ruleset created. |  -  |
**400** | The request is invalid |  -  |
**409** | standalone ruleset already exists. The existing ruleset is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_ruleset_bundle**
> StandaloneRulesetBundle create_standalone_ruleset_bundle(standalone_ruleset_bundle)

Add a standalone ruleset bundle

Adds a new standalone ruleset bundle. rulesets must have unique names within an org. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_ruleset_bundle import StandaloneRulesetBundle
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_bundle = StandaloneRulesetBundle(
        metadata=MetadataWithId(),
        spec=StandaloneRulesetBundleSpec(
            name=StandaloneRulesetBundleName("my-bundles"),
            org_id="123",
            labels=[
                StandaloneRulesetBundleLabel(
                    exclude=True,
                    label=StandaloneRulesetLabelSpec(
                        name=StandaloneRulesetLabelName("agilicus-defaults"),
                        org_id="123",
                    ),
                    priority=0,
                ),
            ],
        ),
        status=StandaloneRulesetBundleStatus(
            standalone_rulesets=[
                StandaloneRulesetInBundle(
                    priority=0,
                    standalone_ruleset=StandaloneRuleset(
                        metadata=MetadataWithId(),
                        spec=StandaloneRulesetSpec(
                            name=StandaloneRuleName("my-rule"),
                            labels=[
                                StandaloneRulesetLabelName("agilicus-defaults"),
                            ],
                            org_id="123",
                            object_conditions=StandaloneObjectConditions(
                                scopes=[
                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                ],
                            ),
                            rule_trees=[
                                StandaloneRuleTreeRef(
                                    rule_tree_name=StandaloneRuleName("my-rule"),
                                    priority=0,
                                ),
                            ],
                            standalone_rule_policy_id="123",
                        ),
                        status=StandaloneRulesetStatus(
                            rule_trees=[
                                StandaloneRuleTree(
                                    metadata=MetadataWithId(),
                                    spec=StandaloneRuleTreeSpec(
                                        name=StandaloneRuleName("my-rule"),
                                        tree=StandaloneRuleTreeNode(
                                            children=[
                                                StandaloneRuleTreeNodeChild(
                                                    priority=0,
                                                    node=StandaloneRuleTreeNode(),
                                                ),
                                            ],
                                            rules=[
                                                StandaloneRuleTreeRuleRef(
                                                    rule_name=StandaloneRuleName("my-rule"),
                                                ),
                                            ],
                                            require_children_true=True,
                                        ),
                                        org_id="123",
                                        object_conditions=StandaloneObjectConditions(
                                            scopes=[
                                                StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                            ],
                                        ),
                                        description="/",
                                        standalone_rule_policy_id="123",
                                    ),
                                    status=StandaloneRuleTreeStatus(
                                        tree=DereferencedStandaloneRuleTreeNode(
                                            children=[
                                                DereferencedStandaloneRuleTreeNodeChild(
                                                    priority=0,
                                                    node=DereferencedStandaloneRuleTreeNode(),
                                                ),
                                            ],
                                            rules=[
                                                StandaloneRule(
                                                    metadata=MetadataWithId(),
                                                    spec=StandaloneRuleSpec(
                                                        rule=RuleConfig(
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
                                                        org_id="123",
                                                        purpose="ag-revocation-proxy",
                                                        standalone_rule_policy_id="123",
                                                    ),
                                                ),
                                            ],
                                            object_conditions=StandaloneObjectConditions(
                                                scopes=[
                                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                                ],
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
            ],
            standalone_rulesets_etag="standalone_rulesets_etag_example",
        ),
    ) # StandaloneRulesetBundle | 

    # example passing only required values which don't have defaults set
    try:
        # Add a standalone ruleset bundle
        api_response = api_instance.create_standalone_ruleset_bundle(standalone_ruleset_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->create_standalone_ruleset_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_bundle** | [**StandaloneRulesetBundle**](StandaloneRulesetBundle.md)|  |

### Return type

[**StandaloneRulesetBundle**](StandaloneRulesetBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New standalone ruleset bundle created. |  -  |
**400** | The request is invalid |  -  |
**409** | standalone ruleset bundle already exists. The existing bundle is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_ruleset_label**
> delete_ruleset_label(label)

Delete a StandaloneRulesetLabel

Delete a StandaloneRulesetLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a StandaloneRulesetLabel
        api_instance.delete_ruleset_label(label)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_ruleset_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a StandaloneRulesetLabel
        api_instance.delete_ruleset_label(label, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_ruleset_label: %s\n" % e)
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
**204** | StandaloneRulesetLabel was deleted |  -  |
**404** | StandaloneRulesetLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_standalone_rule**
> delete_standalone_rule(rule_id)

Delete a standalone rule

Delete a standalone rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    rule_id = "Absadal2" # str | The id of a rule
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a standalone rule
        api_instance.delete_standalone_rule(rule_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a standalone rule
        api_instance.delete_standalone_rule(rule_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
**204** | StandaloneRule was deleted |  -  |
**404** | StandaloneRule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_standalone_rule_policy**
> delete_standalone_rule_policy(standalone_rule_policy_id)

Delete a standalone rule policy

Delete a standalone rule policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_policy_id = "Absadal2" # str | The id of a standalone rule policy
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a standalone rule policy
        api_instance.delete_standalone_rule_policy(standalone_rule_policy_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a standalone rule policy
        api_instance.delete_standalone_rule_policy(standalone_rule_policy_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_policy_id** | **str**| The id of a standalone rule policy |
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
**204** | StandaloneRulePolicy was deleted |  -  |
**404** | StandaloneRulePolicy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_standalone_rule_tree**
> delete_standalone_rule_tree(standalone_rule_tree_id)

Delete a standalone rule tree

Delete a standalone rule tree

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_tree_id = "Absadal2" # str | The id of a rule tree
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a standalone rule tree
        api_instance.delete_standalone_rule_tree(standalone_rule_tree_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule_tree: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a standalone rule tree
        api_instance.delete_standalone_rule_tree(standalone_rule_tree_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_rule_tree: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_tree_id** | **str**| The id of a rule tree |
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
**204** | StandaloneRuleTree was deleted |  -  |
**404** | StandaloneRuleTree does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_standalone_ruleset**
> delete_standalone_ruleset(standalone_ruleset_id)

Delete a standalone ruleset

Delete a standalone ruleset

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_id = "Absadal2" # str | The id of a ruleset
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a standalone ruleset
        api_instance.delete_standalone_ruleset(standalone_ruleset_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_ruleset: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a standalone ruleset
        api_instance.delete_standalone_ruleset(standalone_ruleset_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_ruleset: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_id** | **str**| The id of a ruleset |
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
**204** | StandaloneRuleset was deleted |  -  |
**404** | StandaloneRuleset does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_standalone_ruleset_bundle**
> delete_standalone_ruleset_bundle(standalone_ruleset_bundle_id)

Delete a standalone ruleset_bundle

Delete a standalone ruleset_bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_bundle_id = "Absadal2" # str | The id of a ruleset
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a standalone ruleset_bundle
        api_instance.delete_standalone_ruleset_bundle(standalone_ruleset_bundle_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_ruleset_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a standalone ruleset_bundle
        api_instance.delete_standalone_ruleset_bundle(standalone_ruleset_bundle_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->delete_standalone_ruleset_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_bundle_id** | **str**| The id of a ruleset |
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
**204** | StandaloneRulesetBundle was deleted |  -  |
**404** | StandaloneRulesetBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ruleset_label**
> StandaloneRulesetLabel get_ruleset_label(label)

Get a StandaloneRulesetLabel

Get a StandaloneRulesetLabel

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_ruleset_label import StandaloneRulesetLabel
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
    api_instance = rules_api.RulesApi(api_client)
    label = TrustedCertificateLabelName("1234") # TrustedCertificateLabelName | A TrustedCertificateLabelName
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a StandaloneRulesetLabel
        api_response = api_instance.get_ruleset_label(label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_ruleset_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a StandaloneRulesetLabel
        api_response = api_instance.get_ruleset_label(label, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_ruleset_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label** | **TrustedCertificateLabelName**| A TrustedCertificateLabelName |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**StandaloneRulesetLabel**](StandaloneRulesetLabel.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | StandaloneRulesetLabel found and returned |  -  |
**404** | StandaloneRulesetLabel does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_standalone_rule**
> StandaloneRule get_standalone_rule(rule_id)

Get a standalone rule

Get a standalone rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule import StandaloneRule
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
    api_instance = rules_api.RulesApi(api_client)
    rule_id = "Absadal2" # str | The id of a rule
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a standalone rule
        api_response = api_instance.get_standalone_rule(rule_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a standalone rule
        api_response = api_instance.get_standalone_rule(rule_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**| The id of a rule |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**StandaloneRule**](StandaloneRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a StandaloneRule |  -  |
**404** | StandaloneRule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_standalone_rule_policy**
> StandaloneRulePolicy get_standalone_rule_policy(standalone_rule_policy_id)

Get a standalone rule policy

Get a standalone rule policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule_policy import StandaloneRulePolicy
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_policy_id = "Absadal2" # str | The id of a standalone rule policy
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a standalone rule policy
        api_response = api_instance.get_standalone_rule_policy(standalone_rule_policy_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a standalone rule policy
        api_response = api_instance.get_standalone_rule_policy(standalone_rule_policy_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_policy_id** | **str**| The id of a standalone rule policy |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**StandaloneRulePolicy**](StandaloneRulePolicy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a StandaloneRulePolicy |  -  |
**404** | StandaloneRulePolicy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_standalone_rule_tree**
> StandaloneRuleTree get_standalone_rule_tree(standalone_rule_tree_id)

Get a standalone rule tree

Get a standalone rule tree

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_rule_tree import StandaloneRuleTree
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_tree_id = "Absadal2" # str | The id of a rule tree
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a standalone rule tree
        api_response = api_instance.get_standalone_rule_tree(standalone_rule_tree_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule_tree: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a standalone rule tree
        api_response = api_instance.get_standalone_rule_tree(standalone_rule_tree_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_rule_tree: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_tree_id** | **str**| The id of a rule tree |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**StandaloneRuleTree**](StandaloneRuleTree.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a StandaloneRuleTree |  -  |
**404** | StandaloneRuleTree does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_standalone_ruleset**
> StandaloneRuleset get_standalone_ruleset(standalone_ruleset_id)

Get a standalone ruleset

Get a standalone ruleset

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_ruleset import StandaloneRuleset
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_id = "Absadal2" # str | The id of a ruleset
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a standalone ruleset
        api_response = api_instance.get_standalone_ruleset(standalone_ruleset_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_ruleset: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a standalone ruleset
        api_response = api_instance.get_standalone_ruleset(standalone_ruleset_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_ruleset: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_id** | **str**| The id of a ruleset |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**StandaloneRuleset**](StandaloneRuleset.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a StandaloneRuleset |  -  |
**404** | StandaloneRuleset does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_standalone_ruleset_bundle**
> StandaloneRulesetBundle get_standalone_ruleset_bundle(standalone_ruleset_bundle_id)

Get a standalone ruleset bundle

Get a standalone ruleset bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_ruleset_bundle import StandaloneRulesetBundle
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_bundle_id = "Absadal2" # str | The id of a ruleset
    org_id = "1234" # str | Organisation Unique identifier (optional)
    get_rulesets = True # bool | When querying a bundle, return all rulesets associated with bundle  (optional)
    standalone_rulesets_etag = "asdflkjasf" # str | The entity tag (etag) for a requested bundle. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a standalone ruleset bundle
        api_response = api_instance.get_standalone_ruleset_bundle(standalone_ruleset_bundle_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_ruleset_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a standalone ruleset bundle
        api_response = api_instance.get_standalone_ruleset_bundle(standalone_ruleset_bundle_id, org_id=org_id, get_rulesets=get_rulesets, standalone_rulesets_etag=standalone_rulesets_etag)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->get_standalone_ruleset_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_bundle_id** | **str**| The id of a ruleset |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **get_rulesets** | **bool**| When querying a bundle, return all rulesets associated with bundle  | [optional]
 **standalone_rulesets_etag** | **str**| The entity tag (etag) for a requested bundle. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  | [optional]

### Return type

[**StandaloneRulesetBundle**](StandaloneRulesetBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a StandaloneRulesetBundle |  -  |
**404** | StandaloneRulesetBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_ruleset_labels**
> ListStandaloneRulesetLabelsResponse list_ruleset_labels()

list StandaloneRulesetLabel

List StandaloneRulesetLabel 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.list_standalone_ruleset_labels_response import ListStandaloneRulesetLabelsResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list StandaloneRulesetLabel
        api_response = api_instance.list_ruleset_labels(limit=limit, org_id=org_id, label=label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_ruleset_labels: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]

### Return type

[**ListStandaloneRulesetLabelsResponse**](ListStandaloneRulesetLabelsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a list of StandaloneRulesetLabel |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_standalone_rule_policies**
> ListStandaloneRulePoliciesResponse list_standalone_rule_policies()

List all standalone rule policies

List all standalone rule policies matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.emptiable_object_type import EmptiableObjectType
from agilicus_api.model.list_standalone_rule_policies_response import ListStandaloneRulePoliciesResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    object_type = EmptiableObjectType("abA12") # EmptiableObjectType | An object type (optional)
    object_types = [
        EmptiableObjectType("["abA12"]"),
    ] # [EmptiableObjectType] | A list of object types. Returns all items which match at least one of the types.  (optional)
    object_id = "1234" # str, none_type | search by object id (optional)
    policy_class = "mfa" # str, none_type | search by policy class (optional)
    policy_classes = ["mfa"] # [str] | A list of policy classes. Returns all items which match at least one of the .  (optional)
    policy_instance = "MyStrongPolicy" # str | Query the policies by instance (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone rule policies
        api_response = api_instance.list_standalone_rule_policies(limit=limit, object_type=object_type, object_types=object_types, object_id=object_id, policy_class=policy_class, policy_classes=policy_classes, policy_instance=policy_instance, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_standalone_rule_policies: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **object_type** | **EmptiableObjectType**| An object type | [optional]
 **object_types** | [**[EmptiableObjectType]**](EmptiableObjectType.md)| A list of object types. Returns all items which match at least one of the types.  | [optional]
 **object_id** | **str, none_type**| search by object id | [optional]
 **policy_class** | **str, none_type**| search by policy class | [optional]
 **policy_classes** | **[str]**| A list of policy classes. Returns all items which match at least one of the .  | [optional]
 **policy_instance** | **str**| Query the policies by instance | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListStandaloneRulePoliciesResponse**](ListStandaloneRulePoliciesResponse.md)

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

# **list_standalone_rule_trees**
> ListStandaloneRuleTreesResponse list_standalone_rule_trees()

List all standalone rule trees

List all standalone rule tres matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. Searching for rule_id will return any tree that references that rule. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.list_standalone_rule_trees_response import ListStandaloneRuleTreesResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    rule_tree_id = "Absadal2" # str | The id of a rule tree (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    standalone_rule_policy_ids = ["Absadal2"] # [str] | A list of standalone rule policy ids. Any objects matching one of these will be returned. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone rule trees
        api_response = api_instance.list_standalone_rule_trees(limit=limit, name=name, page_at_id=page_at_id, rule_tree_id=rule_tree_id, org_id=org_id, standalone_rule_policy_ids=standalone_rule_policy_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_standalone_rule_trees: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **rule_tree_id** | **str**| The id of a rule tree | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **standalone_rule_policy_ids** | **[str]**| A list of standalone rule policy ids. Any objects matching one of these will be returned. | [optional]

### Return type

[**ListStandaloneRuleTreesResponse**](ListStandaloneRuleTreesResponse.md)

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

# **list_standalone_rules**
> ListStandaloneRulesResponse list_standalone_rules()

List all standalone rules

List all standalone rule matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.list_standalone_rules_response import ListStandaloneRulesResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    rule_id = "Absadal2" # str | The id of a rule (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    standalone_rule_policy_ids = ["Absadal2"] # [str] | A list of standalone rule policy ids. Any objects matching one of these will be returned. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone rules
        api_response = api_instance.list_standalone_rules(limit=limit, name=name, page_at_id=page_at_id, rule_id=rule_id, org_id=org_id, standalone_rule_policy_ids=standalone_rule_policy_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_standalone_rules: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **rule_id** | **str**| The id of a rule | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **standalone_rule_policy_ids** | **[str]**| A list of standalone rule policy ids. Any objects matching one of these will be returned. | [optional]

### Return type

[**ListStandaloneRulesResponse**](ListStandaloneRulesResponse.md)

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

# **list_standalone_ruleset_bundles**
> ListStandaloneRulesetBundlesResponse list_standalone_ruleset_bundles()

List all standalone ruleset bundles

List all standalone ruleset bundles matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.list_standalone_ruleset_bundles_response import ListStandaloneRulesetBundlesResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)
    get_rulesets = True # bool | When querying a bundle, return all rulesets associated with bundle  (optional)
    standalone_ruleset_bundles_etag = "asdflkjasf" # str | The entity tag (etag) for a list of bundles. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone ruleset bundles
        api_response = api_instance.list_standalone_ruleset_bundles(limit=limit, name=name, page_at_id=page_at_id, org_id=org_id, label=label, get_rulesets=get_rulesets, standalone_ruleset_bundles_etag=standalone_ruleset_bundles_etag)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_standalone_ruleset_bundles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]
 **get_rulesets** | **bool**| When querying a bundle, return all rulesets associated with bundle  | [optional]
 **standalone_ruleset_bundles_etag** | **str**| The entity tag (etag) for a list of bundles. If the returned etag matches the requested etag, then no data is returned, along with status code 304.  | [optional]

### Return type

[**ListStandaloneRulesetBundlesResponse**](ListStandaloneRulesetBundlesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |
**304** | Response not modified |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_standalone_rulesets**
> ListStandaloneRulesetsResponse list_standalone_rulesets()

List all standalone rulesets

List all standalone rulesets matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.list_standalone_rulesets_response import ListStandaloneRulesetsResponse
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
    api_instance = rules_api.RulesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)
    standalone_rule_policy_ids = ["Absadal2"] # [str] | A list of standalone rule policy ids. Any objects matching one of these will be returned. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone rulesets
        api_response = api_instance.list_standalone_rulesets(limit=limit, name=name, page_at_id=page_at_id, org_id=org_id, label=label, standalone_rule_policy_ids=standalone_rule_policy_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->list_standalone_rulesets: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]
 **standalone_rule_policy_ids** | **[str]**| A list of standalone rule policy ids. Any objects matching one of these will be returned. | [optional]

### Return type

[**ListStandaloneRulesetsResponse**](ListStandaloneRulesetsResponse.md)

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

# **replace_standalone_rule**
> StandaloneRule replace_standalone_rule(rule_id)

update a standalone rule

update a standalone rule

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule import StandaloneRule
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
    api_instance = rules_api.RulesApi(api_client)
    rule_id = "Absadal2" # str | The id of a rule
    standalone_rule = StandaloneRule(
        metadata=MetadataWithId(),
        spec=StandaloneRuleSpec(
            rule=RuleConfig(
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
            org_id="123",
            purpose="ag-revocation-proxy",
            standalone_rule_policy_id="123",
        ),
    ) # StandaloneRule |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a standalone rule
        api_response = api_instance.replace_standalone_rule(rule_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a standalone rule
        api_response = api_instance.replace_standalone_rule(rule_id, standalone_rule=standalone_rule)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**| The id of a rule |
 **standalone_rule** | [**StandaloneRule**](StandaloneRule.md)|  | [optional]

### Return type

[**StandaloneRule**](StandaloneRule.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated StandaloneRule |  -  |
**400** | The request is invalid |  -  |
**404** | StandaloneRule does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_standalone_rule_policy**
> StandaloneRulePolicy replace_standalone_rule_policy(standalone_rule_policy_id)

update a standalone rule policy

update a standalone rule policy

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_rule_policy import StandaloneRulePolicy
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_policy_id = "Absadal2" # str | The id of a standalone rule policy
    standalone_rule_policy = StandaloneRulePolicy(
        metadata=MetadataWithId(),
        spec=StandaloneRulePolicySpec(
            org_id="123",
            object_type=EmptiableObjectType("desktop"),
            object_id="123",
            policy_class="mfa",
            policy_instance="default-mfa-policy",
            description=StandaloneRulePolicyDescription("/"),
            annotations={},
        ),
    ) # StandaloneRulePolicy |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a standalone rule policy
        api_response = api_instance.replace_standalone_rule_policy(standalone_rule_policy_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule_policy: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a standalone rule policy
        api_response = api_instance.replace_standalone_rule_policy(standalone_rule_policy_id, standalone_rule_policy=standalone_rule_policy)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule_policy: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_policy_id** | **str**| The id of a standalone rule policy |
 **standalone_rule_policy** | [**StandaloneRulePolicy**](StandaloneRulePolicy.md)|  | [optional]

### Return type

[**StandaloneRulePolicy**](StandaloneRulePolicy.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated StandaloneRulePolicy |  -  |
**400** | The request is invalid |  -  |
**404** | StandaloneRulePolicy does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_standalone_rule_tree**
> StandaloneRuleTree replace_standalone_rule_tree(standalone_rule_tree_id)

update a standalone rule tree

update a standalone rule tree

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_rule_tree import StandaloneRuleTree
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_rule_tree_id = "Absadal2" # str | The id of a rule tree
    standalone_rule_tree = StandaloneRuleTree(
        metadata=MetadataWithId(),
        spec=StandaloneRuleTreeSpec(
            name=StandaloneRuleName("my-rule"),
            tree=StandaloneRuleTreeNode(
                children=[
                    StandaloneRuleTreeNodeChild(
                        priority=0,
                        node=StandaloneRuleTreeNode(),
                    ),
                ],
                rules=[
                    StandaloneRuleTreeRuleRef(
                        rule_name=StandaloneRuleName("my-rule"),
                    ),
                ],
                require_children_true=True,
            ),
            org_id="123",
            object_conditions=StandaloneObjectConditions(
                scopes=[
                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                ],
            ),
            description="/",
            standalone_rule_policy_id="123",
        ),
        status=StandaloneRuleTreeStatus(
            tree=DereferencedStandaloneRuleTreeNode(
                children=[
                    DereferencedStandaloneRuleTreeNodeChild(
                        priority=0,
                        node=DereferencedStandaloneRuleTreeNode(),
                    ),
                ],
                rules=[
                    StandaloneRule(
                        metadata=MetadataWithId(),
                        spec=StandaloneRuleSpec(
                            rule=RuleConfig(
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
                            org_id="123",
                            purpose="ag-revocation-proxy",
                            standalone_rule_policy_id="123",
                        ),
                    ),
                ],
                object_conditions=StandaloneObjectConditions(
                    scopes=[
                        StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                    ],
                ),
            ),
        ),
    ) # StandaloneRuleTree |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a standalone rule tree
        api_response = api_instance.replace_standalone_rule_tree(standalone_rule_tree_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule_tree: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a standalone rule tree
        api_response = api_instance.replace_standalone_rule_tree(standalone_rule_tree_id, standalone_rule_tree=standalone_rule_tree)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_rule_tree: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_rule_tree_id** | **str**| The id of a rule tree |
 **standalone_rule_tree** | [**StandaloneRuleTree**](StandaloneRuleTree.md)|  | [optional]

### Return type

[**StandaloneRuleTree**](StandaloneRuleTree.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated StandaloneRuleTree |  -  |
**400** | The request is invalid |  -  |
**404** | StandaloneRuleTree does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_standalone_ruleset**
> StandaloneRuleset replace_standalone_ruleset(standalone_ruleset_id)

update a standalone ruleset

update a standalone ruleset

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.standalone_ruleset import StandaloneRuleset
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_id = "Absadal2" # str | The id of a ruleset
    standalone_ruleset = StandaloneRuleset(
        metadata=MetadataWithId(),
        spec=StandaloneRulesetSpec(
            name=StandaloneRuleName("my-rule"),
            labels=[
                StandaloneRulesetLabelName("agilicus-defaults"),
            ],
            org_id="123",
            object_conditions=StandaloneObjectConditions(
                scopes=[
                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                ],
            ),
            rule_trees=[
                StandaloneRuleTreeRef(
                    rule_tree_name=StandaloneRuleName("my-rule"),
                    priority=0,
                ),
            ],
            standalone_rule_policy_id="123",
        ),
        status=StandaloneRulesetStatus(
            rule_trees=[
                StandaloneRuleTree(
                    metadata=MetadataWithId(),
                    spec=StandaloneRuleTreeSpec(
                        name=StandaloneRuleName("my-rule"),
                        tree=StandaloneRuleTreeNode(
                            children=[
                                StandaloneRuleTreeNodeChild(
                                    priority=0,
                                    node=StandaloneRuleTreeNode(),
                                ),
                            ],
                            rules=[
                                StandaloneRuleTreeRuleRef(
                                    rule_name=StandaloneRuleName("my-rule"),
                                ),
                            ],
                            require_children_true=True,
                        ),
                        org_id="123",
                        object_conditions=StandaloneObjectConditions(
                            scopes=[
                                StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                            ],
                        ),
                        description="/",
                        standalone_rule_policy_id="123",
                    ),
                    status=StandaloneRuleTreeStatus(
                        tree=DereferencedStandaloneRuleTreeNode(
                            children=[
                                DereferencedStandaloneRuleTreeNodeChild(
                                    priority=0,
                                    node=DereferencedStandaloneRuleTreeNode(),
                                ),
                            ],
                            rules=[
                                StandaloneRule(
                                    metadata=MetadataWithId(),
                                    spec=StandaloneRuleSpec(
                                        rule=RuleConfig(
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
                                        org_id="123",
                                        purpose="ag-revocation-proxy",
                                        standalone_rule_policy_id="123",
                                    ),
                                ),
                            ],
                            object_conditions=StandaloneObjectConditions(
                                scopes=[
                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                ],
                            ),
                        ),
                    ),
                ),
            ],
        ),
    ) # StandaloneRuleset |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a standalone ruleset
        api_response = api_instance.replace_standalone_ruleset(standalone_ruleset_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_ruleset: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a standalone ruleset
        api_response = api_instance.replace_standalone_ruleset(standalone_ruleset_id, standalone_ruleset=standalone_ruleset)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_ruleset: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_id** | **str**| The id of a ruleset |
 **standalone_ruleset** | [**StandaloneRuleset**](StandaloneRuleset.md)|  | [optional]

### Return type

[**StandaloneRuleset**](StandaloneRuleset.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated StandaloneRuleset |  -  |
**400** | The request is invalid |  -  |
**404** | StandaloneRuleset does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_standalone_ruleset_bundle**
> StandaloneRulesetBundle replace_standalone_ruleset_bundle(standalone_ruleset_bundle_id)

update a standalone ruleset bundle

update a standalone ruleset bundle

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import rules_api
from agilicus_api.model.standalone_ruleset_bundle import StandaloneRulesetBundle
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
    api_instance = rules_api.RulesApi(api_client)
    standalone_ruleset_bundle_id = "Absadal2" # str | The id of a ruleset
    standalone_ruleset_bundle = StandaloneRulesetBundle(
        metadata=MetadataWithId(),
        spec=StandaloneRulesetBundleSpec(
            name=StandaloneRulesetBundleName("my-bundles"),
            org_id="123",
            labels=[
                StandaloneRulesetBundleLabel(
                    exclude=True,
                    label=StandaloneRulesetLabelSpec(
                        name=StandaloneRulesetLabelName("agilicus-defaults"),
                        org_id="123",
                    ),
                    priority=0,
                ),
            ],
        ),
        status=StandaloneRulesetBundleStatus(
            standalone_rulesets=[
                StandaloneRulesetInBundle(
                    priority=0,
                    standalone_ruleset=StandaloneRuleset(
                        metadata=MetadataWithId(),
                        spec=StandaloneRulesetSpec(
                            name=StandaloneRuleName("my-rule"),
                            labels=[
                                StandaloneRulesetLabelName("agilicus-defaults"),
                            ],
                            org_id="123",
                            object_conditions=StandaloneObjectConditions(
                                scopes=[
                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                ],
                            ),
                            rule_trees=[
                                StandaloneRuleTreeRef(
                                    rule_tree_name=StandaloneRuleName("my-rule"),
                                    priority=0,
                                ),
                            ],
                            standalone_rule_policy_id="123",
                        ),
                        status=StandaloneRulesetStatus(
                            rule_trees=[
                                StandaloneRuleTree(
                                    metadata=MetadataWithId(),
                                    spec=StandaloneRuleTreeSpec(
                                        name=StandaloneRuleName("my-rule"),
                                        tree=StandaloneRuleTreeNode(
                                            children=[
                                                StandaloneRuleTreeNodeChild(
                                                    priority=0,
                                                    node=StandaloneRuleTreeNode(),
                                                ),
                                            ],
                                            rules=[
                                                StandaloneRuleTreeRuleRef(
                                                    rule_name=StandaloneRuleName("my-rule"),
                                                ),
                                            ],
                                            require_children_true=True,
                                        ),
                                        org_id="123",
                                        object_conditions=StandaloneObjectConditions(
                                            scopes=[
                                                StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                            ],
                                        ),
                                        description="/",
                                        standalone_rule_policy_id="123",
                                    ),
                                    status=StandaloneRuleTreeStatus(
                                        tree=DereferencedStandaloneRuleTreeNode(
                                            children=[
                                                DereferencedStandaloneRuleTreeNodeChild(
                                                    priority=0,
                                                    node=DereferencedStandaloneRuleTreeNode(),
                                                ),
                                            ],
                                            rules=[
                                                StandaloneRule(
                                                    metadata=MetadataWithId(),
                                                    spec=StandaloneRuleSpec(
                                                        rule=RuleConfig(
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
                                                        org_id="123",
                                                        purpose="ag-revocation-proxy",
                                                        standalone_rule_policy_id="123",
                                                    ),
                                                ),
                                            ],
                                            object_conditions=StandaloneObjectConditions(
                                                scopes=[
                                                    StandaloneRuleScope("urn:agilicus:application:guid:role:self"),
                                                ],
                                            ),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ),
                ),
            ],
            standalone_rulesets_etag="standalone_rulesets_etag_example",
        ),
    ) # StandaloneRulesetBundle |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a standalone ruleset bundle
        api_response = api_instance.replace_standalone_ruleset_bundle(standalone_ruleset_bundle_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_ruleset_bundle: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a standalone ruleset bundle
        api_response = api_instance.replace_standalone_ruleset_bundle(standalone_ruleset_bundle_id, standalone_ruleset_bundle=standalone_ruleset_bundle)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling RulesApi->replace_standalone_ruleset_bundle: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **standalone_ruleset_bundle_id** | **str**| The id of a ruleset |
 **standalone_ruleset_bundle** | [**StandaloneRulesetBundle**](StandaloneRulesetBundle.md)|  | [optional]

### Return type

[**StandaloneRulesetBundle**](StandaloneRulesetBundle.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated StandaloneRulesetBundle |  -  |
**400** | The request is invalid |  -  |
**404** | StandaloneRulesetBundle does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

