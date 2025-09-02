# RuleSet

A RuleSet collects rules into a tree which so that nested rules may be evaluated in a well-defined manner. These trees are typically built from explicit configuration (e.g. nested child_rules within a RulesConfig). A RuleSet contains a node and a list of children. The node is the parent to the children. If there are no children, then this RuleSet is a leaf. A node corresponds to a RuleConfig, and the children correspond to the RuleConfig objects associated to the RuleConfig via a RuleSetComponent. A node with no parents is a root. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node** | [**RuleSetNode**](RuleSetNode.md) |  | 
**children** | [**[RuleSet]**](RuleSet.md) | The children of &#x60;node&#x60; as determined from the associated RuleSetComponent list.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


