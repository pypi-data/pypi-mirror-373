# SupportRequestSpec

Configuration containing properties associated with a support request that is allowed to provide support to the organisation. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**supporting_user_org_id** | **str** | Unique identifier | [optional] 
**supporting_user_email** | [**Email**](Email.md) |  | [optional] 
**expiry** | **datetime** | The support group time in UTC. Defaults to support group created time + 24h | [optional] 
**viewer_only_permissions** | **bool** | Whether or not this support group is allowed to make modifications in this organisation A value of true indicates that the support group is not allowed  | [optional] 
**admin_state** | **str** | The state of the support request.  Whether the user has access, has requested access, etc. The possible values have the following meanings:   - pending: the support request is pending   - active: the support request is still active   - terminated: the support request is terminated, group is deleted   - expired: the support request is expired  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


