# UpstreamGroupReconcile

The input parameters required to reconcile a user's groups with the groups from their upstream identity provider. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the user within the system. | 
**org_id** | **str** | The unique id of the Organisation from which to apply a reconcile. This applies to the org specified and all of that org&#39;s sub-orgs.  | 
**mapping** | [**UpstreamGroupMapping**](UpstreamGroupMapping.md) |  | 
**group_names_from_upstream** | **[str]** | The list of group names that the user is in from the perspective of the upstream identity provider. | [optional] 
**group_guids_from_upstream** | **[str]** | The list of group GUIDs that the user is in from the perspective of the upstream identity provider. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


