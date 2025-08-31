# MessageSendItem

A message to send and information about how to route it

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | [**Message**](Message.md) |  | 
**addresses** | [**[MessageAddress]**](MessageAddress.md) | The message will be sent to each of these addresses.  | 
**ephemeral** | **bool** | Whether or not the message should be fire and forget, or whether it should be persisted for some time.  | 
**endpoint_types** | [**[MessageEndpointType]**](MessageEndpointType.md) | The types of endpoint to send to. If not specified, defaults to [inbox, webpush]  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


