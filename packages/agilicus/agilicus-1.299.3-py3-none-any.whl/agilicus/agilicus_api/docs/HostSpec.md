# HostSpec

The specification for a Host. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hostname** | [**Domain**](Domain.md) |  | 
**port** | [**NetworkPort**](NetworkPort.md) |  | [optional] 
**path** | **str** | An optional path specific to this hostname entry. This field is optional and implementation specific, and its usage is dependent on the client implementation wishing to lookup a particular hostname + path.  | [optional] 
**labels** | [**[HostLabelName]**](HostLabelName.md) | list of labels associated with host | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


