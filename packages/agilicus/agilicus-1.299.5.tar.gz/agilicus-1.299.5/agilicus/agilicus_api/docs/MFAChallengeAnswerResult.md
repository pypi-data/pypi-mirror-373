# MFAChallengeAnswerResult

The result of an MFAChallengeQuestion

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | **str** | The action to take as a result of the question. do_mfa - the user should be challenged to present a second factor for authentication dont_mfa - the user does not need to present a second factor for authentication. Proceed with the login workflow. This is depricated in favour of allow_login deny_login - the user should not be allowed to proceed. Terminate the login. allow_login - the user should be allowed to proceed with the login workflow. authenticate - the user should be directed to authenticate with the system typically via an upstream identity provider  | 
**supported_mfa_methods** | **[str]** | The list of supported multi-factor challenge methods for the organisation | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


