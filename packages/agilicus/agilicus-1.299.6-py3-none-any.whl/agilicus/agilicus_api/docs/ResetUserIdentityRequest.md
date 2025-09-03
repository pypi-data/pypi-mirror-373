# ResetUserIdentityRequest

Resets a user to use a new set of core properties. Doing this will remove many of their preferences (such as multifactor settings) so be sure to only do so if truly desired. Only users who belong to a single Organisation may be reset this way.  The user's identifier will be changed to the value of new_identifier if no other users in the system share it. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The unique id of the Organisation to which this user belongs.  | 
**new_identifier** | [**Email**](Email.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


