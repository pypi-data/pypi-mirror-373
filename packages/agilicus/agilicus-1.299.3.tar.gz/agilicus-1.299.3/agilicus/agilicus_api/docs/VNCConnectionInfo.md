# VNCConnectionInfo

The configuration required by the connector to connect to the vnc server

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**password_authentication_info** | [**VNCPasswordAuthentication**](VNCPasswordAuthentication.md) |  | [optional] 
**disable_gateway** | **bool** | By default, the connector runs a gateway which tries to adapt the client and server&#39;s vnc protocols into mutually compatible versions. Occasionally this process can choose the wrong settings, leading to an unworkable VNC desktop. Setting this to true disables that functionality. Note that this could break deployments which otherwise worked, so it should only be used when necessary.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


