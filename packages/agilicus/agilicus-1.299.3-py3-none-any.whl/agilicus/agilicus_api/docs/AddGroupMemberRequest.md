# AddGroupMemberRequest

Request object to add a new group member

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**member_id** | **str** | Unique identifier | [optional] 
**member_org_id** | **str** | Unique identifier | [optional] 
**email** | [**Email**](Email.md) |  | [optional] 
**upstream_issuer** | **str** | the upstream issuer associated with this group. This field is set if this user was added to the group via an upstream issuer mapping rule.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


