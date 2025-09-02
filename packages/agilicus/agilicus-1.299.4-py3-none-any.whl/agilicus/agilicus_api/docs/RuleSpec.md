# RuleSpec

The definition of a rule. Contains all information that controls how the rule behaves. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_id** | **str** | Unique identifier | [optional] 
**comments** | **str** | A description of the rule. The comments have no functional effect, but can help to clarify the purpose of a rule when the name is not sufficient.  | [optional] 
**condition** | [**HttpRule**](HttpRule.md) |  | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**scope** | [**RuleScopeEnum**](RuleScopeEnum.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


