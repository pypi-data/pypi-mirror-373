# SessionChallengeMessage

A message sent to a user so that they can respond to a session challenge. This contains the session challenge, as well as a token which may be used to respond to the challenge. The returned token can *only* be used for responding to the challenge. It has no other use, and times out in the same time range as the challenge itself. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_challenge** | [**SessionChallenge**](SessionChallenge.md) |  | 
**token** | **str** | The token to use when responding to the session challenge. This token will time out soon after the challenge times out.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


