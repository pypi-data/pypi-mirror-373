# StandaloneRuleTreeSpec

Definition of a StandaloneRuleTree. The spec contains a tree, which recursively defines a tree of rules. Name is used to help with human identificaction of the rule, but is not necessary. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**StandaloneRuleName**](StandaloneRuleName.md) |  | 
**tree** | [**StandaloneRuleTreeNode**](StandaloneRuleTreeNode.md) |  | 
**org_id** | **str** | Unique identifier | 
**object_conditions** | [**StandaloneObjectConditions**](StandaloneObjectConditions.md) |  | [optional] 
**description** | **str** | A description of the purpose of the StandaloneRuleTree. Use this to provide more context for why the rule exists, any complexities or decisions related to it, etc.  | [optional] 
**standalone_rule_policy_id** | **str, none_type** | A unique identifier which can be empty. The meaning of it being empty depends on the context in which it is used, but usually it implies that something is not set.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


