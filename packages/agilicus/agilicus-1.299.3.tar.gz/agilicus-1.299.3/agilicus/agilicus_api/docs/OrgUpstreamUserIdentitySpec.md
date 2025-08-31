# OrgUpstreamUserIdentitySpec

Specification for OrgUpstreamUserIdentity 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the user within the system. This is the user to which this identity is tied.  | 
**org_id** | **str** | The unique id of the organisation to which this record applies.  | 
**identity_id** | **str** | Unique identifier | 
**last_login** | **datetime** | The last login time for this user, specific to the upstream identity.  | [optional] 
**user_attributes** | [**UserAttributes**](UserAttributes.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


