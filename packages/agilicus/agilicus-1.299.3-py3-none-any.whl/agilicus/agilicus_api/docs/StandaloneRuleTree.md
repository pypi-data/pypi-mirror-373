# StandaloneRuleTree

Builds a tree of rules evaluated by the rule engine top-down, using a preorder depth first search. The engine only evaluates child nodes if the containing node's rules evaluate to true. At that point, the rules engine evaluates the child and its siblings in priority order, stopping on the first match. The separation the rule definitions (StandaloneRule) from how they are related (StandaloneRuleTree), allows for reuse of basic building block rules in various contexts. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**StandaloneRuleTreeSpec**](StandaloneRuleTreeSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**StandaloneRuleTreeStatus**](StandaloneRuleTreeStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


