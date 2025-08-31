# MessageEndpointType

The output medium to use. Not all medium are equally able to use all fields. All support `text`. In the event of medium which don't support anything other than `text`, the `uri` field is appended with `context` added as a parameter. Examples are web_push, sms, ... The inbox type queues the message in a per-user inbox. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The output medium to use. Not all medium are equally able to use all fields. All support &#x60;text&#x60;. In the event of medium which don&#39;t support anything other than &#x60;text&#x60;, the &#x60;uri&#x60; field is appended with &#x60;context&#x60; added as a parameter. Examples are web_push, sms, ... The inbox type queues the message in a per-user inbox.  |  must be one of ["web_push", "sms", "inbox", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


