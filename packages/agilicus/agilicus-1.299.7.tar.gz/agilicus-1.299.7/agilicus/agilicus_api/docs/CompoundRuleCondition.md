# CompoundRuleCondition

A CompoundRuleCondition combines multiple RuleConditions in Conjunctive Normal Form (AND) or Disjunctive Normal Form (OR). Using the CompoundRuleCondition, a user can express complicated logical statements by recursively combining CompoundRuleConditions with varying settings of the `list_type` and `negation` (in the RuleCondition) fields.  A CompoundRuleCondition is true based on the truth of the conditions in its list and the type of list it has. `list_type` controls the evaluation of the CompoundRuleCondition as follows:   - `cnf`: Conjunctive Normal Form. If all RuleCondition in the `condition_list` is true, then the     CompoundRuleCondition is true. Otherwise, it is false. That is, the expression may be viewed as:       `condition_list[0] AND condition_list[1] AND ... AND condition_list[len(condition_list) - 1]`   - `dnf`: Disjunctive Normal Form. If any RuleCondition in the `condition_list` is true, then the     CompoundRuleCondition is true. If no RuleConditions are true, then the CompoundRuleCondition is false.     That is, the expression may be viewed as:       `condition_list[0] OR condition_list[1] OR ... OR condition_list[len(condition_list) - 1]`  Note that the conditions in the `condition_list` may be evaluated in any order.  CompoundRuleConditions may not be nested more than 4 levels deep. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**condition_list** | [**[RuleCondition]**](RuleCondition.md) | The list of conditions whose truth determines the truth of the CompoundRuleCondition. How that the conditions&#39; truth is combined depends on &#x60;list_type&#x60;.  | 
**list_type** | **str** | How to combine the truth of the conditions in &#x60;condition_list&#x60; to determine the overall truth of the CompoundRuleCondition. - &#x60;cnf&#x60;: Conjunctive Normal Form. The conditions are combined using an AND operator. - &#x60;dnf&#x60;: Disjunctive Normal Form. The conditions are combined using an OR operator.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


