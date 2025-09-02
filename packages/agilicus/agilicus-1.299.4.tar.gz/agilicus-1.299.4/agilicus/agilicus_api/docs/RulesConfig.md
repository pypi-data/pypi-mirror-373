# RulesConfig

The rules configuration for a Resource. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rules** | [**[RuleConfig]**](RuleConfig.md) | The list of rules associated with this resource. | [optional] 
**rule_set_components** | [**[RuleSetComponent]**](RuleSetComponent.md) | A list of RuleSetComponents which build a forest of RuleSet trees. Each node of a RuleSet contains a single RuleConfig, and a list of child RuleSets. RuleSets evaluate top down, using a preorder depth first search. Child rules will only be evaluated if the containing rule&#39;s condition evaluates to true. At that point, they will be evaluated in priority order. Actions taken by child rules will be evaluated in order, after any actions added by the containing rule.  All child rules of a parent rule are evaluated regardless of whether or not they are assigned to a role applicable to the evaluation context. For example, if a user has role X, rule A is in role X, and has child rule B which is in role Y, evaluation of rule A will also evaluate rule B (if necessary), despite rule B not independently being part of role X.  If a containing rule and a child rule have roles in common, they will only be evaluated once in the context of the outermost containing role. This allows rules to be applied to roles independently when necessary, while deterministically defining the rule evaluation.  A RuleSet MUST be a tree. Thus, there can be no cycles within the structure: no rule may refer to itself, and no child rule can refer to an ancestor rule.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


