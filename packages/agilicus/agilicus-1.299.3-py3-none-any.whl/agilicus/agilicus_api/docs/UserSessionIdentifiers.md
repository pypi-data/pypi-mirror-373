# UserSessionIdentifiers

parameters used to constrain which sessions will be acted on. (Revoked, deleted, etc)

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the User associated with the session  | 
**org_id** | **str** | The unique id of the Organisation associated with the Issuer the user logged in to  | [optional] 
**session_id** | **str** | The unique id of an explicit session to revoke.  | [optional] 
**tokens_only** | **bool** | Controls whether to revoke only the tokens, keeping the session live. If true, all related tokens are revoked, but the session is left intact. False by default. This setting lets you revoke any outstanding logins associated with this session -- as part of forcing a logout, for example, while still allowing the user to log in with the saved session.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


