# RoleV2

A Role collects a set of rules together. A user with a given role has the permissions granted by the rules it collects. A Role can include other roles to include the rules they collect into its own. Typically a Role represents a functional role within an Organisation. E.g. administrator, auditor, etc. A role is globally identified by its ID. Within an application, its name must be unique. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**RoleSpec**](RoleSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


