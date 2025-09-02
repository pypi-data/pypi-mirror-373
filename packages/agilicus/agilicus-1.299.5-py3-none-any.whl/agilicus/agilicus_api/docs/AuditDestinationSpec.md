# AuditDestinationSpec

The specification of an AuditDestination

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to sent events to the AuditDestination at all. Setting &#x60;enabled&#x60; to &#x60;false&#x60; will direct all event sources to stop sending events to the AuditDestination.  | 
**name** | **str** | A descriptive name for the destination. This will be used in reporting and diagnostics.  | 
**org_id** | **str** | Unique identifier | 
**destination_type** | **str** | The type of the destination. This controls how events are sent to the destination. This can be set to the following values:  - &#x60;file&#x60;: A file destination. The url is the path to a file on disk where events will be logged. The log format is JSONL. The log file is rotated. Old rotations are placed in the same directory as the log file. - &#x60;webhook&#x60;: A webhook destination. The url is points to an http server which will accept POSTs of an   AuditWebhookEvent object. The server should respond with an HTTP 2XX return code on success. The   event should be handled as a transaction: either all events are processed, or none. An HTTP 429   in conjunction with a Retry-After header may be used to tell the audit agent to back off. An HTTP   400 will instruct the audit agent to discard all of the events.  | 
**location** | **str** | The location of the destination. The meaning of the location changes based on the destination type.  - &#x60;file&#x60;: A URL of the path to the file on the local system. The URL should be of the form &#x60;file:///path/to/file&#x60;.    On Windows this can be &#x60;/drive/path/to/file&#x60;.  If the path is relative (&#x60;file://./path/to/file&#x60;), the relative path is    rooted at the directory from which the evnet source is running.  | 
**comment** | **str** | A short comment describing the purpose of the destination. This is only used for informational purposes.  | 
**filters** | [**[AuditDestinationFilter]**](AuditDestinationFilter.md) | The list of filters controlling which events are sent to this destination. All filters must pass in order to send an event to this destination.  | 
**max_events_per_transaction** | **int** | The maximum number of events to emit to destination in one transaction. If unspecified, the value is unlimited. This can be useful if the destination (e.g. a webhook) has a maximum request size.  | [optional] 
**authentication** | [**AuditDestinationAuthentication**](AuditDestinationAuthentication.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


