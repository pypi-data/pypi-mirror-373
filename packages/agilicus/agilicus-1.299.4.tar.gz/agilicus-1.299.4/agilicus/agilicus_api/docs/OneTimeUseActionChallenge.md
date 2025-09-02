# OneTimeUseActionChallenge

A challenge which when answered will take a programmatic action, such as making an HTTP request. This action may be configured to act on behalf of a particular user by retrieving a short lived token with a predefined set of scopes. Parameters of the action such as an HTTP body are also configurable. The main purpose of a OneTimeUseActionChallenge is to allow a user to take an action such as approving a request without needing to log in to the system. Proof of the user's ability to do this is obtained via the challenge being delivered to the user over a trusted channel such as webpush or message inboxes.  Creating a OneTimeUseActionChallenge creates a Challenge which may be associated with a user so they can poll it for completion. That challenge tracks the status of the challenge.  The response to creating a OneTimeUseActionChallenge contains the values needed to answer the challenge. The caller is responsible for forwarding these to the appropriate users while ensuring secrecy. The challenge itself is associated with a particular user so that they may poll it for its status.  Multiple actors may answer the challenge. Each actor is provided their own challenge answer to ensure that we can uniquely identify who answered the challenge. This mechanism allows an action to be taken by exactly one of many users -- whoever gets to it first -- while providing each user as little capability as necessary to take the action.  Once created the challenge cannot be modified. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**OneTimeUseActionChallengeSpec**](OneTimeUseActionChallengeSpec.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


