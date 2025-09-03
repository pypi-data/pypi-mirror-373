# MessageEndpointsConfig

A list of the registered message endpoint types, and their config.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sms** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | The configuration of the sms endpoint type.  | [optional] 
**web_push** | [**MessageEndpointTypeWebPush**](MessageEndpointTypeWebPush.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


