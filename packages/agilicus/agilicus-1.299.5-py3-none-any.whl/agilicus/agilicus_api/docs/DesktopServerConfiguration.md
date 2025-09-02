# DesktopServerConfiguration

Contains the information used to generate a configuration file for a server exposing a desktop. For example, this can be used to generate registry entries for configuring RemoteApp desktops. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The ID of the organisation which owns this DesktopResource.  | 
**configuration_file_format** | [**ConfigFileFormat**](ConfigFileFormat.md) |  | 
**generated_config** | [**DesktopServerGeneratedConfiguration**](DesktopServerGeneratedConfiguration.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


