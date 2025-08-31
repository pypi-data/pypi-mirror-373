# ResourcePermission

A ResourcePermission describes a user's permission (aka role) for a specific resource in a given organisation. The meaning of a permission for a given resource depends on the type of the resource itself, but generally the permission will allow interaction with the system described by the resource. For example, a permission related to a FileShare resource will grant the user permission to interact with the files exposed by that particular file share. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**ResourcePermissionSpec**](ResourcePermissionSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


