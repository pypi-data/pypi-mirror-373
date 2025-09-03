# PolicySpec

The definition of the policy.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issuer_id** | **str, none_type** | The issuer that this policy applies to | 
**supported_mfa_methods** | **[str]** | A list of supported MFA methods. An empty list implies that no MFA methods are acceptable | 
**default_action** | **str** | The action to take if none of the conditions evaluate to true. Actions are case sensitive. | 
**name** | **str** | The name of the policy so that it can be identifiable when applied to organizations or clients | [optional] 
**org_id** | **str** | The org id corresponding to the issuer whose policy you are updating | [optional] 
**rules** | [**[PolicyRule]**](PolicyRule.md) | The list of rules defining the policy. A rule consists of conditions, actions, and a priority | [optional] [readonly] 
**policy_groups** | [**[PolicyGroup]**](PolicyGroup.md) | A list of policy groups ordered by priority. The first item in the list represents the group with the highest priority. A policy group consists of a list of rules. All rules in a group of higher priority will have higher precedence than any rule in a group of lower priority.  | [optional] 
**source** | **str** | An identifier for the policy this policy was based on. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


