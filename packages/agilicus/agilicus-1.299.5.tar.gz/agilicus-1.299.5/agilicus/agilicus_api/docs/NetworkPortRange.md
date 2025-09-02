# NetworkPortRange

A definition of transport-layer port(s) on which to access a service.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**port** | [**NetworkPort**](NetworkPort.md) |  | 
**protocol** | **str** | The transport-layer protocol over which to communicate with the service.  | defaults to "tcp"
**alternate_mode_setting** | [**LearningModeSpec**](LearningModeSpec.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


