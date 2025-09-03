# MFAEnrollmentAnswerResult

The result of an MFAEnrollmentQuestion

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | **str** | The action to take as a result of the question. enroll - the user should be prompted to enroll a multi-factor authentication method dont_enroll - the user does not need to enroll a multi-factor authentication method enrollment_error - the user would be prompted to enroll but is unable to enroll. An example of this is if the enrollment request is outside the time window allowed by an organisation  | 
**supported_mfa_methods** | **[str]** | The list of supported multi-factor challenge methods for the organisation | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


