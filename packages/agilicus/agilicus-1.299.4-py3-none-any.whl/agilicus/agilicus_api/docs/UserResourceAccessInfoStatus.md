# UserResourceAccessInfoStatus

The read-only details of a UserFileShareAcessInfo.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the User to which this record applies.  | 
**org_id** | **str** | The unique id of the Organisation to which this record applies.  | 
**org_name** | **str** | The name of Organisation to which this record applies.  | 
**resource_id** | **str** | Unique identifier | 
**resource_name** | **str** | The name of the resource.  | 
**resource_type** | **str** | The type of the resource.  | 
**access_level** | **str** | Whether the user has access, has requested access, etc. The possible values have the following meanings:   - requested: the user has requested access to this resource.   - granted: the user has access to this resource   - none: the user has no relation to this resource.  | 
**parent_org_id** | **str** | The unique id of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**parent_org_name** | **str** | The name of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**resource_uri** | **str** | Many resources have corresponding URIs which may be used to access them. This field provides the URI for the resource represented by this object.  | [optional] 
**roles** | **[str]** | The list of roles held by the user for the given resource. | [optional] 
**display_info** | [**DisplayInfo**](DisplayInfo.md) |  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


