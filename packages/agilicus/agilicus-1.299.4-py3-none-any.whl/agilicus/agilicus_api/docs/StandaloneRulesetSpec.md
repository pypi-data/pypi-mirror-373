# StandaloneRulesetSpec

The specification of the StandaloneRuleset. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**StandaloneRuleName**](StandaloneRuleName.md) |  | 
**labels** | [**[StandaloneRulesetLabelName]**](StandaloneRulesetLabelName.md) | A list of labels within this organisation to associated with the StandaloneRuleset  | 
**org_id** | **str** | Unique identifier | 
**rule_trees** | [**[StandaloneRuleTreeRef]**](StandaloneRuleTreeRef.md) |  | 
**object_conditions** | [**StandaloneObjectConditions**](StandaloneObjectConditions.md) |  | [optional] 
**standalone_rule_policy_id** | **str, none_type** | A unique identifier which can be empty. The meaning of it being empty depends on the context in which it is used, but usually it implies that something is not set.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


