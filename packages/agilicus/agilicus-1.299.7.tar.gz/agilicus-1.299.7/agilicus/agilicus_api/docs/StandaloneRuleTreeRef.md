# StandaloneRuleTreeRef

A reference to a StandaloneRuleTree to be included elsewhere. Priority defines the order in which the tree is evaluated in the included context. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rule_tree_name** | [**StandaloneRuleName**](StandaloneRuleName.md) |  | 
**priority** | **int** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


