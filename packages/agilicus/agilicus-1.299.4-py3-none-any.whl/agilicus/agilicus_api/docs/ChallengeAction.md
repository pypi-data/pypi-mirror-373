# ChallengeAction


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**challenge_action_type** | **str** | The descriminator for a ChallengeAction. set to \&quot;http_action\&quot; | 
**body** | **str** | The concent to use for the request if needed | [optional] 
**content_type** | **str** | The content-type of the body | [optional] 
**scopes** | [**[TokenScope]**](TokenScope.md) | The scopes to request in the access token used for the request. If this array is empty, then no access token is requested.  | [optional] 
**method** | **str** | The method to use for the request | [optional] 
**uri** | **str** | The URI of the request | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


