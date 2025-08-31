# VNCPasswordAuthentication

Password configuration for the connector to authenticate to the vnc server. Note that standard VNC authentication only supports passwords of length 8. Longer will be truncated when authenticating. The system will try its best to negotatiate a stronger authentication mechanism with the VNC server, thereby enabling longer passwords, but it may fall back on standard VNC authentication. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**read_write_password** | **str** | The password which enables a vnc connection with enables user input | [optional] 
**read_write_username** | **str** | The username to use when connecting with user control. | [optional] 
**read_only_password** | **str** | The password which enables a vnc connection with no user control | [optional] 
**read_only_username** | **str** | The username to use when connecting with no user control | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


