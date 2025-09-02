# HttpRule

A rule condition applied to the attributes of an http request.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rule_type** | **str** | Used to distinguish between different types of rule | 
**condition_type** | **str** | The descriminator for an HttpRuleCondition | [optional] 
**methods** | **[str]** | The HTTP methods to allow. If any of the listed methods are matched, then this portion of the rule matches.  | [optional] 
**path_regex** | **str** | regex for HTTP path. Can be templatized with jinja2 using definitions collection. | [optional] 
**path_template** | [**TemplatePath**](TemplatePath.md) |  | [optional] 
**query_parameters** | [**[RuleQueryParameter]**](RuleQueryParameter.md) | A set of constraints on the parameters specified in the query string. | [optional] 
**body** | [**RuleQueryBody**](RuleQueryBody.md) |  | [optional] 
**matchers** | [**RuleMatcherList**](RuleMatcherList.md) |  | [optional] 
**separate_query** | **bool** | Whether or not to include the query parameter in path operations such as regex matches. If &#x60;true&#x60;, then the query parameter will be treated as separate from the path. Otherwise, if the path constraints will evaluate all of the query parameters as part of the http path. For example, if a regex path constraint is &#x60;^/part1/part2$&#x60; and separate_query is true, then an input path of &#x60;/part1/part2?key&#x3D;value&#x60; will pass. However, if separate_query is false, it will fail. If not present, defaults to false.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


