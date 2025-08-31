# MaxMFAProofRuleCondition

This condition is evaluated against the users last mfa proof time, and if that time has exceeded, the condition evaluates to true. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**max_seconds** | **int** | The max number of seconds allowed before MFA is required.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


