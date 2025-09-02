# CreateTokenRequest

Request object to create a token

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sub** | **str** | Unique identifier | 
**org** | **str** | Unique identifier | 
**audiences** | **[str]** | array of audiences | 
**time_validity** | [**TimeValidity**](TimeValidity.md) |  | 
**roles** | **{str: (str,)}** | associative mapping of an application to a role | [optional] 
**hosts** | [**[HostPermissions]**](HostPermissions.md) | array of valid hosts | [optional] 
**token_validity** | [**TokenValidity**](TokenValidity.md) |  | [optional] 
**session** | **str** | Unique identifier | [optional] 
**scopes** | [**[TokenScope]**](TokenScope.md) | The list of scopes requested for the access token. Multiple scopes are seperated by a space character. Ex. urn:agilicus:users urn:agilicus:issuers. An optional is specified with an ? at the end. Optional scopes are used when the permission is requested but not required. Ex. urn:agilicus:users? | [optional] 
**inherit_session** | **bool** | When session is not provided, this option controls if the session applied to the token should come from the token making the token create request. This option is normally True, so that all tokens are chained together using the same session. This would normally be set to False when creating system orientated tokens so that they have no session, and subsequently, tokens created with this sessionless token will also not contain an inherited token (unless of course it was created with the session in the payload of the request).  | [optional]  if omitted the server will use the default value of True
**create_refresh_token** | **bool** | If true, also create and return a refresh token that allows the created token to be specifically refreshed.  | [optional] 
**get_user** | **bool** | If true, the Raw token will also return the user record  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


