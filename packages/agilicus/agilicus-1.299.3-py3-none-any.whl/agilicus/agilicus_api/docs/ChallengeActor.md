# ChallengeActor

Specifies a user who can approve a challenge. An action approved by this actor will be done using credentials associated with the given user_id and org_id. Note that if the user does not have permission to take the action, the action will fail. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | Unique identifier | 
**org_id** | **str** | Unique identifier | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


