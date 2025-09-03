# RenderedRule

Rendered rule

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**methods** | **[str]** | The HTTP method to allow. | [optional] 
**paths** | **[str]** | regex for HTTP path. | [optional] 
**template_paths** | [**[TemplatePath]**](TemplatePath.md) | A list of template paths to match against. The first match in the list will be used. Be careful if they overlap: put more precise paths first in the list. A template can be used to provide information for more precise matchers as configured by http_extractors.  | [optional] 
**query_parameters** | [**[RenderedQueryParameter]**](RenderedQueryParameter.md) | A set of constraints on the parameters contained in the query string. | [optional] 
**body** | [**RenderedRuleBody**](RenderedRuleBody.md) |  | [optional] 
**resource_info** | [**ResourceInfo**](ResourceInfo.md) |  | [optional] 
**matchers** | [**RuleMatcherList**](RuleMatcherList.md) |  | [optional] 
**separate_query** | **bool** | Whether or not to include the query parameter in path operations such as regex matches. If &#x60;true&#x60;, then the query parameter will be treated as separate from the path. Otherwise, if the path constraints will evaluate all of the query parameters as part of the http path. For example, if a regex path constraint is &#x60;^/part1/part2$&#x60; and separate_query is true, then an input path of &#x60;/part1/part2?key&#x3D;value&#x60; will pass. However, if separate_query is false, it will fail.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


