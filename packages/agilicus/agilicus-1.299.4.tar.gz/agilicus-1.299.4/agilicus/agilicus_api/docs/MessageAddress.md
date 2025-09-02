# MessageAddress

Describes to whom to send a message.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | Unique identifier | 
**org_id** | **str** | Unique identifier | [optional] 
**direct** | **bool** | Whether to send directly to the user, or to its members. By default, if not present, this is false, meaning the message will be sent to members of this user if the user is a group.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


