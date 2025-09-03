# MFAEnrollmentQuestionLoginInfo

A question to the Open Policy Agent to determine if a multi-factor authentication enrollment should occur.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issuer_org_id** | **str** | The id of the organisation for the issuer the user is logging in through. This determines what policy to query | 
**enrollment_expiry** | **datetime** | The expiry time for multi-factor authentication enrollment. Requests to enroll outside this time bound will be denied. | 
**user_mfa_methods** | **[str]** | The list of multi-factor challenge methods the user has set up. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


