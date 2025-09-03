# RuleConditionBase


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**methods** | **[str]** | The HTTP methods to allow. If any of the listed methods are matched, then this portion of the rule matches.  | [optional] 
**path_regex** | **str** | regex for HTTP path. Can be templatized with jinja2 using definitions collection. | [optional] 
**path_template** | [**TemplatePath**](TemplatePath.md) |  | [optional] 
**query_parameters** | [**[RuleQueryParameter]**](RuleQueryParameter.md) | A set of constraints on the parameters specified in the query string. | [optional] 
**body** | [**RuleQueryBody**](RuleQueryBody.md) |  | [optional] 
**matchers** | [**RuleMatcherList**](RuleMatcherList.md) |  | [optional] 
**separate_query** | **bool** | Whether or not to include the query parameter in path operations such as regex matches. If &#x60;true&#x60;, then the query parameter will be treated as separate from the path. Otherwise, if the path constraints will evaluate all of the query parameters as part of the http path. For example, if a regex path constraint is &#x60;^/part1/part2$&#x60; and separate_query is true, then an input path of &#x60;/part1/part2?key&#x3D;value&#x60; will pass. However, if separate_query is false, it will fail. If not present, defaults to false.  | [optional] 
**prefix** | **str** | A case-sensitive, absolute prefix to match against. The prefix cannot contain a query string.  | [optional] 
**rule_type** | **str** | Used to distinguish between different types of rule | [optional] 
**condition_list** | [**[RuleCondition]**](RuleCondition.md) | The list of conditions whose truth determines the truth of the CompoundRuleCondition. How that the conditions&#39; truth is combined depends on &#x60;list_type&#x60;.  | [optional] 
**list_type** | **str** | How to combine the truth of the conditions in &#x60;condition_list&#x60; to determine the overall truth of the CompoundRuleCondition. - &#x60;cnf&#x60;: Conjunctive Normal Form. The conditions are combined using an AND operator. - &#x60;dnf&#x60;: Disjunctive Normal Form. The conditions are combined using an OR operator.  | [optional] 
**operator** | **str** | How to evaluate the variable against the value. - &#x60;in&#x60;: set membership. Checks that variable is in value, assuming value is a list. - &#x60;not_in&#x60;: set anti-membership. Checks that variable is in value, assuming value is a list.  | [optional] 
**value** | **[str]** | The set of country codes to check against | [optional] 
**host** | **str** | A case insensitive host or IP address, possibly including a port. Note that if the host is an empty string, then it s considered a trivial match.  | [optional] 
**max_seconds** | **int** | The max number of seconds allowed before MFA is required.  | [optional] 
**scopes** | [**[StandaloneRuleScope]**](StandaloneRuleScope.md) | The list of scopes where if one is true, the condition will be true  | [optional] 
**subnets** | **[str]** | The list of subnets to check | [optional] 
**protocol** | **str** | The specific protocol.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


