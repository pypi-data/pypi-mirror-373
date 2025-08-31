# CombinedRulesStatus

The status contents of a combined rule. Since the rule is synthesized, this will contain the majority of its information. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_id** | **str** | Unique identifier | [optional] [readonly] 
**org_id** | **str** | Unique identifier | [optional] [readonly] 
**role_id** | **str** | Unique identifier | [optional] [readonly] 
**role_name** | **str** | The name of the role under which these rules were combined. If no role was associated with the rules, will be empty.  | [optional] 
**rules** | [**[RuleV2]**](RuleV2.md) | The rules combined together by the common property indicated by scope or role_id  | [optional] 
**scope** | [**RuleScopeEnum**](RuleScopeEnum.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


