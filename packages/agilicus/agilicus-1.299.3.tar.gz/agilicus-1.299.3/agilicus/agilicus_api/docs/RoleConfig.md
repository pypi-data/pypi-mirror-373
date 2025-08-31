# RoleConfig

A RoleConfig defines a role that is used to grant permission(s) to a UserIdentity. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_name** | **str** | A short descriptive name used to identify the role. Role names must be unique within a resource.  | 
**default** | **bool** | If True, this role will be assigned to users granted access to this resource by default, (unless overridden). In the case of multiple roles defined for a resource, only a single role is permitted as default. If multiple roles are requested as default, the API will return 400.  | [optional]  if omitted the server will use the default value of False
**builtin** | **bool** | This role is builtin and is managed by the the system.  | [optional] [readonly] 
**description** | **str** | A brief description of the role detailing the purpose of the role and what sort of permissions it grants.  | [optional] 
**included_roles** | **[str]** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


