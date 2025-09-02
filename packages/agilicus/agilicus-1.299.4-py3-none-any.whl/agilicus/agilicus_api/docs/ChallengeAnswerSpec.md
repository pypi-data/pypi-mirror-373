# ChallengeAnswerSpec

The contents of the challenge answer. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**answer** | **str** | An opaque string used to answer the challenge. | 
**challenge_id** | **str** | The id of the challenge being answered. This is not required. It is present for consistency.  | [optional] 
**answer_data** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | An object containing an arbitrary set of data for this challenge. This is useful for when you want to convey information over the challenge in a one-time use fashion. E.g. perhaps you have a secret and some extra information about it. They can be packaged up in this. Note that it is unstructured so that it can be used for any usecase, as long as the two sides of the challenge agree on the format.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


