# UserRequestUserUpdate

Updates the status of a user in response to a user request. Can also be used to reset te permissions of the user as part of approving a request so that only the permissions assigned as part of the request take effect.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The unique id of the organisation to which this record applies.  | 
**user_id** | **str** | The unique id of the User to which this record applies.  | 
**new_status** | [**UserStatusEnum**](UserStatusEnum.md) |  | 
**reset_permissions** | **bool** | Whether or not to reset the user&#39;s permissions. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


