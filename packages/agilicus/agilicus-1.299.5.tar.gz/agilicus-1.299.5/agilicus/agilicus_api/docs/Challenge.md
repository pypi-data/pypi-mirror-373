# Challenge

An authentication challenge. These are short lived resources which track the state of a authentication challenge in the system. They are created when a challenge response workflow starts, and persist for some time after the response completes. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**ChallengeSpec**](ChallengeSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**ChallengeStatus**](ChallengeStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


