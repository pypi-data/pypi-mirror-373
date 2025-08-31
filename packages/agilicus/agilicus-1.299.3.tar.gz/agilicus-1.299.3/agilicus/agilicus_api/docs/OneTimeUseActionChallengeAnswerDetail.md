# OneTimeUseActionChallengeAnswerDetail

Provides the details needed to answer the challenge for a given actor. Ensure that the answer can only be seen/viewed by the associated actor. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actor** | [**ChallengeActor**](ChallengeActor.md) |  | 
**approve_uri** | **str** | The URI to GET in order to approve the challenge. Accessing this URI will trigger the one-time use action for approval. Keep this URI secret.  | 
**decline_uri** | **str** | The URI to GET in order to decline the challenge. Accessing this URI will trigger the one-time use action for declining. Keep this URI secret.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


