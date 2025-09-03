# RuleSetNode

A node within a RuleSet. This is essentially the dereferenced version of a RuleSetComponent. That is, it contains the child referred to by name of a RuleSetComponent and its priority. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rule** | [**RuleConfig**](RuleConfig.md) |  | 
**priority** | **int** | The priority of the rule relative to sibling rules in the RuleSet. Rules are evaluated in order of higher priority number to lower priority number.  | defaults to 0
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


