# ScopeCondition

This condition is true if the request satisfies at least one of the provided scopes. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**scopes** | [**[StandaloneRuleScope]**](StandaloneRuleScope.md) | The list of scopes where if one is true, the condition will be true  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


