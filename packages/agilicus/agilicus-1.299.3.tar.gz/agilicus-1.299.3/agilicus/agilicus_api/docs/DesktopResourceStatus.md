# DesktopResourceStatus

Derived, read-only properties of a DesktopResource. Use these to determine how to interact with a DesktopResource, or to see its current state. If you have not assigned the DesktopResource to a Connector, then some of its status will not be availble. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway_uri** | **str** | The uri at which to access the Desktop Gateway for this DesktopResource.  | 
**stats** | [**DesktopResourceStats**](DesktopResourceStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


