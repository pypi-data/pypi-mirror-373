# DesktopResource

A desktop exposed via the Agilicus Cloud. Access the desktop using a client, supporting a protocol such as the Remote Desktop Protocol, by way of a Desktop Gateway. You may expose multiple desktops by creating multiple DesktopResource objects. A Connector provides connectivity between the Agilicus Cloud and your desktop so that you do not have to expose the desktop to the Internet.  A desktop may actually be a remote application. If a remote_app is defined for a desktop, then launching the desktop will always launch the remote application; it will not be used to connect to the full desktop environment. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**DesktopResourceSpec**](DesktopResourceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**DesktopResourceStatus**](DesktopResourceStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


