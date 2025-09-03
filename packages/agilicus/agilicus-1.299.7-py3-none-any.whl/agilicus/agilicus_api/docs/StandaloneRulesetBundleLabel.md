# StandaloneRulesetBundleLabel

A label that is part of a bundle and its associated operation. The rulesets in the bundle will be evaluated in priority order according to the priority associated with the label that brought them into the set. If the ruleset matches multiple label, it will take the lowest matching priority. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | [**StandaloneRulesetLabelSpec**](StandaloneRulesetLabelSpec.md) |  | 
**exclude** | **bool** | if true, the rulesets with the label are excluded from the bundle. When a label is excluded, it takes precendence over included rules, such that if a ruleset were to labeled with both an exclude and not exclude label, the result would be for that ruleset to be excluded.  | [optional] 
**priority** | **int** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


