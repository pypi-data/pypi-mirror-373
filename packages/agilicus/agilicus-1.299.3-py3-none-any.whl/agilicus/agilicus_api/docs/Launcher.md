# Launcher

Object describing the properties of a Launcher. A launcher encompasses the configuration for launching a program via an agent connector, allowing the launched program's requests to be proxied through Agilicus to the corresponding backend resources.  For example, an ERP system has an installed client on a computer, that uses network services, ie. TCP port(s). 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**spec** | [**LauncherSpec**](LauncherSpec.md) |  | [optional] 
**status** | [**LauncherStatus**](LauncherStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


