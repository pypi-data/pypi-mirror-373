# LauncherSpec

Object describing the spec of a Launcher

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The launcher name. A launcher name must match to the following regular expression:   &#x60;^[a-zA-Z0-9-_ ]+$&#x60;  | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**resource_members** | [**[ResourceMember]**](ResourceMember.md) | The resources that are necessary for this Launcher to run. For example, it could be an ApplicationServices using TCP port(s), or FileShareServices. | [optional] 
**config** | [**LauncherConfig**](LauncherConfig.md) |  | [optional] 
**applications** | **[str]** | The associated applications that this launcher may launch. | [optional] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**alternate_mode_setting** | [**AlternateModeSetting**](AlternateModeSetting.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


