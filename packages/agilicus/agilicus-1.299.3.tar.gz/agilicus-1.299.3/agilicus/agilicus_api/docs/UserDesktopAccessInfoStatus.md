# UserDesktopAccessInfoStatus

The read-only details of a UserDesktopAccessInfo.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the User to which this record applies.  | 
**org_id** | **str** | The unique id of the Organisation to which this record applies.  | 
**org_name** | **str** | The name of Organisation to which this record applies.  | 
**resource_id** | **str** | Unique identifier | 
**resource_name** | **str** | The name of the resource.  | 
**resource_type** | **str** | The type of the resource.  | 
**desktop_type** | **str** | The type of the desktop | 
**access_level** | **str** | Whether the user has access, has requested access, etc. The possible values have the following meanings:   - requested: the user has requested access to this resource.   - granted: the user has access to this resource   - none: the user has no relation to this resource.  | 
**parent_org_id** | **str** | The unique id of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**parent_org_name** | **str** | The name of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**resource_uri** | **str** | Many resources have corresponding URIs which may be used to access them. This field provides the URI for the resource represented by this object.  | [optional] 
**roles** | **[str]** | The list of roles held by the user for the given resource. | [optional] 
**remote_app** | [**RemoteAppAccessInfo**](RemoteAppAccessInfo.md) |  | [optional] 
**display_info** | [**DisplayInfo**](DisplayInfo.md) |  | [optional] 
**web_client_uri** | **str** | The uri for launching user&#39;s resource via web client  | [optional] 
**config_overrides** | [**[CustomDesktopClientConfig]**](CustomDesktopClientConfig.md) | Configuration overrides applicable to this desktop. If the configured overrides are invalid, this list will be empty, and config_overrides_error will be populated.  | [optional] 
**config_overrides_error** | **str, none_type** | If the system encounters an invalid CustomDesktopClientConfig associated with this desktop, then the corresponding error will be provided here for ease of diagnostics. If this value is not empty, the client should not proceed with creating configuration for the desktop.  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


