# BulkUserRequestApproval

A BulkUserRequestApproval allows a client to approve (or decline) a number of user requests at once, as well as making minor changes to a user state. This method is more efficient than individually approving each UserRequest.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The unique id of the organisation to which the approvals will take effect. Any approvals in the list which do match this org id will be ignored.  | 
**user_updates** | [**[UserRequestUserUpdate]**](UserRequestUserUpdate.md) | A list of users to update. Their org_id must match the org_id provided in this object.  | 
**user_requests** | [**[UserRequestInfo]**](UserRequestInfo.md) | A list of user requests to approve or decline. Whether or not they are approved or declined is controlled by setting their status in the individual UserRequestInfo. The actual properties of the request (e.g. assigned permission) may be modified this way as well.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


