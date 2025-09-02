# RuleSetComponent

An association object linking a parent rule to a child rule. This object assocates the parent rule to a child rule along with a priority describing how the child rule should be evaluated in relation to other rules. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parent_rule_name** | **str** | The name of the parent rule. The rule must exist in the rules_config of the resource.  | 
**child_rule_name** | **str** | The name of the child rule. The rule must exist in the rules_config of the resource.  | 
**priority** | **int** | The priority of the child rule relative to sibling nodes of a RuleSet. Rules are evaluated in order of higher priority number to lower priority number.  | defaults to 0
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


