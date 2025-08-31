# ResourcePermissionSpec

A ResourcePermissionSpec provides the details of a ResourcePermission

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the user which has this permission. | 
**org_id** | **str** | The unique id of the Organisation which the user must be logged in to in order to access the resource with this permission.  | 
**resource_id** | **str** | The unique id of the resource to which the user is granted access. | 
**resource_type** | **str** | The type of the resource referred to by &#x60;resource_id&#x60;. | 
**resource_role_name** | **str** | The unique id of the role assigned to the user. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


