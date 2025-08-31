# APIKeyStatus

Runtime information about the APIKey. The jti is the ID of the token corresponding to this API Key. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token_id** | **str** | Unique identifier | 
**api_key** | **str** | The value to use as the password in the basic authentication flow. Note that this value will only be present in the APIKeyStatus when creating the API Key. It is omitted in future requests to prevent it from leaking. Treat this key like any other password: keep it secret; keep it safe.  | [optional] 
**creating_sub** | **str** | The id of the user who created this APIKey, if different from the APIKey&#39;s sub.  | [optional] 
**creating_org** | **str** | The id of the org of the user who created this APIKey, if that user is different from the token&#39;s sub.  | [optional] 
**masquerading** | **bool** | Whether or not this APIKey was created by a user masquerading as the sub of this APIKey. A masquerading APIKey is constrained in what it can do compared to a normal one: certain operations cannot be performed unless the user has fully authenticated.  | [optional] 
**oper_status** | [**APIKeyOpStatus**](APIKeyOpStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


