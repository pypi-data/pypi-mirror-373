# RuleConfig

A Rule defines a set of conditions which, if matched, allow a request to proceed through the system. If no rules match, the request will be denied. The Rule is a base class, with more concrete classes specifying precise match conditions. Rules may be associated with roles to allow for users to be granted collections of rules. Rules are uniquely identified by their id.  Note that `condition` is deprected. Use the http_rule_condition within extended_condition instead. If both fields are defined, the `condition will be evaluated alongside the `extended_condition` as though the two were part of a `CompoundRuleCondition` using DNF. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the rule. | 
**roles** | **[str]** | The list of roles assigned to this rule. | [optional] 
**excluded_roles** | **[str]** | The list of roles excluded from this rule. | [optional] 
**comments** | **str** | A description of the rule. The comments have no functional effect, but can help to clarify the purpose of a rule when the name is not sufficient.  | [optional] 
**condition** | [**HttpRule**](HttpRule.md) |  | [optional] 
**scope** | [**RuleScopeEnum**](RuleScopeEnum.md) |  | [optional] 
**extended_condition** | [**RuleCondition**](RuleCondition.md) |  | [optional] 
**priority** | **int** | The priority of the rule relative to other rules at the top level: that is, if this rule is not being evaluated as part of a RuleSet, it is assumed to be within a &#39;global&#39; RuleSet that contains all &#39;root&#39; rules. In that case, this priority applies.  Rules are evaluated in order of higher priority number to lower priority number.  | [optional]  if omitted the server will use the default value of 0
**actions** | [**[RuleAction]**](RuleAction.md) | The actions to take if the rule evaluates to true. At least one of allow or deny must be present in the action list for the system to effectively operate on the request. By default, if neither allow nor deny is present in the list of actions resulting from the rule, the request will be allowed. Some actions may conflict.  If there is a conflict, the first action in the preorder depth-first-search traversal of the rule tree will take precedence. For example, deny and allow are conflicting actions. If the parent rule has deny, and a sub_rule has allow, then the request will be denied. Or, if the parent rule has none, the first sub-rule has allow, and the second sub-rule has deny, the request will be allowed.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


