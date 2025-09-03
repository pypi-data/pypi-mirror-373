# StandaloneRulesetInBundle

A container object describing how a StandaloneRuleset is included in a bundle. The priority describes the priority at which the ruleset was ultimately included. A null priority is treated as the lowest possible priority. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**priority** | **int, none_type** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | 
**standalone_ruleset** | [**StandaloneRuleset**](StandaloneRuleset.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


