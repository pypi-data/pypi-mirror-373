# Rule

Rule's properties

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A meaningful name to help identifiy the rule. This may be used to refer to it elsewhere, or to at a glace understand its purpose.  | 
**method** | **str** | The HTTP method to allow. | 
**path** | **str** | regex for HTTP path. Can be templatized with jinja2 using definitions collection. | 
**host** | **str** | hostname to apply authz rule to. Deprecated. This is now inferred from the Environment or Service to which the rule belongs.  | [optional] 
**query_parameters** | [**[RuleQueryParameter]**](RuleQueryParameter.md) | A set of constraints on the parameters specified in the query string. | [optional] 
**body** | [**RuleQueryBody**](RuleQueryBody.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


