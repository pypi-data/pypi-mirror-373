# StandaloneRuleTreeNode

A node in a StandaloneRuleTree. Evaluation of a StandaloneRuleTree starts from its `tree` node. A given node first evaluates all of its `rules`. If they all evaluated to true, or the list is empty, then the `children` nodes are evaluated in priority order. Evaluation halts if one of the `rules` is false, or the `children` are empty. Actions are evaluated in the top-down order. I.e. actions defined by a parent are evaluated before actions defined by a child. Priority must be unique with the list of children. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**children** | [**[StandaloneRuleTreeNodeChild]**](StandaloneRuleTreeNodeChild.md) | The children of this node. They are evaluated in the order specified by their priority. Each child is itself a tree, evaluated recursively.  | 
**rules** | [**[StandaloneRuleTreeRuleRef]**](StandaloneRuleTreeRuleRef.md) | The references of rules for this node. If each rule in this list evaluates to true, then the children of this node are evaluated.  | 
**require_children_true** | **bool** | the default case &#39;false&#39;, if the children to not evaluate to true, the result is still true since the root (rules) was true. However to change this behavior and requiret the children to also be true for the final result to be true, set this property to true. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


