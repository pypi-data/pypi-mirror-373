# AuditWebhookBulkEvent

An collection of audit events emitted by an Agilicus audit agent. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**events** | [**[AuditEvent]**](AuditEvent.md) | The list of events. Set the destination&#39;s &#x60;max_events_per_transaction&#x60; to limit the number.  | 
**always_respond_with_events** | **bool** | Whether to respond with the events from the request, even if they were all succesfully processed.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


