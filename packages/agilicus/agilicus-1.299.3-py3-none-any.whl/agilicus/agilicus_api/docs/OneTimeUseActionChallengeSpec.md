# OneTimeUseActionChallengeSpec

Specifies the details of the OneTimeUseActionChallenge. Note that the user_id corresponds to a user who can poll the challenge for completion. This is typically used in some sort of approval workflow where the user needs to wait for someone else to take action. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**approved_actions** | [**[ChallengeAction]**](ChallengeAction.md) | The list of actions to take when the challenge is approved | 
**declined_actions** | [**[ChallengeAction]**](ChallengeAction.md) | The list of actions to take when the challenge is declined | 
**actors** | [**[ChallengeActor]**](ChallengeActor.md) | The list of users who can approve or decline the challenge. | 
**timeout_seconds** | **int** | For how long the system will accept answers for the challenge. After this time, if the challenge is not in the &#x60;challenge_passed&#x60; state, it will transition into the &#x60;timed_out&#x60; state.  | 
**user_id** | **str** | Unique identifier | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


