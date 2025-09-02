# AuditEvent

An audit event emitted by an Agilicus audit agent. The primary contents of the event are free-form to allow for easy extension. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**unique_id** | **str** | A unique ID that can be used to determine whether the event has been processed multiple times. This should never happen, but it can&#39;t hurt to be safe.  | 
**create_time** | **datetime** | When the event was initially processed. | 
**event** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | The primary contents of the audit event | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


