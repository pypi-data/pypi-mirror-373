# ApplicationUpstreamValidation

Describes how to validate that an application login was successful. The authorization system makes the login request on behalf of the user and validates the http response code and optionally a set of cookies returned match the properties specified below. This is to ensure the login was successful and thus the users identity can be asserted to All cookies must be set if cookie based validation is used. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**successful_response_code** | **int** | the expected http response code the application returns on a successful login | 
**expected_cookies** | **[str]** | the names of the various cookies the application sets on a successful login | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


