# AuditWebhookEventsProcessed

Describes the webhook events which were processed. For ease of error handling, the events are split into separate arrays, each indicating what should should be done with the events: either throw them away because they were processed, throw them away because they are bad, or retry them later. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success_events** | [**[AuditEventResponse]**](AuditEventResponse.md) | The list of events which were succesfully processed. Note that this may be empty. If so, assume that any events not in the other lists were succesfully processed.  | 
**discard_events** | [**[AuditEventResponse]**](AuditEventResponse.md) | The list of events which were discarded. Do not send them again, as they will continue to be discarded.  | 
**retry_events** | [**[AuditEventResponse]**](AuditEventResponse.md) | The list of events to retry. Consult &#x60;retry_after_date&#x60; and &#x60;retry_after_delay_seconds&#x60; for a hint to on when to try again.  | 
**retry_after_date** | **datetime** | If any events are in the &#x60;retry_events&#x60; list, this can hint as to a good time to retry. Note that a &#x60;Retry-After&#x60; header can be used to convey this information as well.  | [optional] 
**retry_after_delay_seconds** | **float** | If any events have the &#x60;too_busy&#x60; status, this can hint as to a delay to wait before trying again. The value is is fractional seconds. Note that a &#x60;Retry-After&#x60; header can be used to convey this information as well.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


