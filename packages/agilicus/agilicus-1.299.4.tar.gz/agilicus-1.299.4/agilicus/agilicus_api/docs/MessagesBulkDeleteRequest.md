# MessagesBulkDeleteRequest

A MessagesBulkDeleteRequest allows a client to delete a number of messages and inbox items associated to it at once. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_tag** | [**MessageTag**](MessageTag.md) |  | [optional] 
**limit** | **int** | The maximum number of messages to delete.  | [optional]  if omitted the server will use the default value of 5000
**delete_expired** | **bool** | If true, delete only expired messages. This is useful to clean up messages which are no longer relevant.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


