# SessionStatus

Session status

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**challenge_id** | **str** | challenge id associated with session | [optional] 
**last_mfa_time** | **int** | Time since the epoch, in seconds, when a multifactor challenge associated with this token was last succesfully performed. If not set then no successfully multifactor challenge is associated with this token.  | [optional] 
**webpush_sent** | **int** | the number of webpush challenge requests sent for this session | [optional] 
**last_webpush** | **datetime** | date-time of the most recent webpush that was sent | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


