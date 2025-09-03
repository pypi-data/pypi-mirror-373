# ResourceStatus

The status object for a Resource. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_stats** | [**ResourceStats**](ResourceStats.md) |  | [optional] 
**all_roles** | [**[RoleConfig]**](RoleConfig.md) | The list of all roles that can be used to assign permissions to a user. This list includes builtin roles as well as the roles defined by this resource object in the ResourceSpec.  | [optional] 
**resource_members** | [**[Resource]**](Resource.md) | The list of all resources that are members of this resource. Note this property is not populated unless expand_member_resources&#x3D;True is provided as a parameter.  | [optional] 
**resource_urls** | [**[ResourceURL]**](ResourceURL.md) | Externally accessible URLs for this resource.  | [optional] 
**ruleset_label** | **str** | The ruleset label utilized for this resource.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


