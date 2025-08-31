# Message

A message to be delivered to a user. This is inspired by Material Cards (https://material.io/components/cards#anatomy), but, constrained by specific output methods. SMS can only deliver a string. WebPush can deliver a Card. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | The text string of the message | 
**id** | **str** | Unique identifier | [optional] [readonly] 
**title** | **str** | The title of the message (if medium allows) | [optional] 
**sub_header** | **str** | The sub-header of the message (if medium allows) | [optional] 
**icon** | **str** | The icon (uri) of the message (if medium allows) | [optional] 
**image** | **str** | The image (uri) of the message (if medium allows) | [optional] 
**uri** | **str** | The overall uri of the message (eg if clicked on). In some medium (e.g. Chrome WebPush) we can have individual actions, in others (e.g. Firefox WebPush) we only get the entire message as link.  | [optional] 
**context** | **str** | A blob of context, message-type dependent | [optional] 
**actions** | [**[MessageAction]**](MessageAction.md) | A list of action buttons (if supported) | [optional] 
**message_type** | [**MessageType**](MessageType.md) |  | [optional] 
**message_class** | [**MessageClass**](MessageClass.md) |  | [optional] 
**expiry_date** | **datetime** | An optional expiry time for the message. An expired message may be deleted at any point by the system.  | [optional] 
**tag** | [**MessageTag**](MessageTag.md) |  | [optional] 
**push_probability** | **float** | The probability the message will be pushed to a user when an event occurs. A value of 1.0 means there is a 100% chance that the message will be pushed. A value of 0.0 means that there is a 0% chance.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


