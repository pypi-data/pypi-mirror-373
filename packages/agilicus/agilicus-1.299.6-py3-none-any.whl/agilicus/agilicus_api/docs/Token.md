# Token

Object describing the properties of a token

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sub** | **str** | Unique identifier | [optional] [readonly] 
**sub_email** | [**Email**](Email.md) |  | [optional] 
**org** | **str** | Unique identifier | [optional] [readonly] 
**root_org** | **str** | The organisation at the root of the hierachy for which this token provides permissions.  | [optional] [readonly] 
**roles** | [**Roles**](Roles.md) |  | [optional] 
**jti** | **str** | Unique identifier | [optional] [readonly] 
**iat** | **str** | token issue date | [optional] [readonly] 
**exp** | **str** | token expiry date | [optional] [readonly] 
**hosts** | [**[HostPermissions]**](HostPermissions.md) | array of valid hosts | [optional] 
**aud** | **[str]** | token audience | [optional] [readonly] 
**session** | **str** | Unique identifier | [optional] [readonly] 
**scopes** | [**[TokenScope]**](TokenScope.md) | The list of scopes associated with this access token. Note that these scopes do not indicate whether that permission has been granted. Whether or not the permission has been granted to this token depends on the scope being associated with the token AND whether the user has that permission to begin with.  | [optional] 
**creating_sub** | **str** | The id of the user who created this token, if different from the token&#39;s sub.  | [optional] [readonly] 
**creating_org** | **str** | The id of the org of the user who created this token, if that user is different from the token&#39;s sub.  | [optional] [readonly] 
**masquerading** | **bool** | Whether or not this token was created by a user masquerading as the sub of this token. A masquerading token is constrained in what it can do compared to a normal one: certain operations cannot be performed unless the user has fully authenticated.  | [optional] [readonly] 
**resource_permissions** | [**[ResourcePermissionSpec]**](ResourcePermissionSpec.md) | The resource permissions associated with this token. The token determines te permissions by cross referencing the user&#39;s permissions with the requested scopes. This list contains only permissions a user has, and only permissions requested by the token&#39;s scopes.  | [optional] 
**user** | [**User**](User.md) |  | [optional] 
**last_mfa_time** | **int** | Time since the epoch, in seconds, when a multifactor challenge associated with this token was last succesfully performed. If not set then no successfully multifactor challenge is associated with this token.  | [optional] 
**refresh_token_jti** | **str** | This token is specifically a refresh token, and can refresh the specified token jti which is this property.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


