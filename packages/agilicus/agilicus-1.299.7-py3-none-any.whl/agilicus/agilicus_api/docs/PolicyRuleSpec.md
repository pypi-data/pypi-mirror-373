# PolicyRuleSpec

A rule to be evaluated by the policy engine.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | **str** | The action to take if the conditions are evaluated to true. Actions are case sensitive. | 
**conditions** | [**[PolicyCondition]**](PolicyCondition.md) | An array mapping a condition type to a condition. | 
**name** | **str** | A descriptive name of the policy rule to help administrators identify each rule. A name should describe the business logic the rule is satisfying. | [optional] 
**priority** | **int** | This field is deprecated. The priority of this rule relative to other rules. Rules of a higher priority will be evaluated first and if the condition evaluates to true the action will be taken. 1 is the highest priority. | [optional]  if omitted the server will use the default value of 1
**org_id** | **str** | The org id corresponding to the issuer whose policy you are updating | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


