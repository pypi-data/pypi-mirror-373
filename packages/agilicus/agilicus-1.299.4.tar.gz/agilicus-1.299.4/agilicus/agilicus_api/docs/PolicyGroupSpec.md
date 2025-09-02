# PolicyGroupSpec

A policy group consists of a list of rules.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rule_ids** | **[str]** | A list of PolicyRule ids that make up the policy group. The rules are evaluated based on the priority of their action. The ordering is as follows allow_login, deny_login, dont_mfa, authenticate, do_mfa The first rule that matches will take that rules action.  | 
**name** | **str** | The name of the group | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


