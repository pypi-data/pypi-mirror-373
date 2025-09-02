# UpstreamGroupReconcileResponse

The response object returned from an upstream group reconcile

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups_added_to** | [**[GroupReconcileRecord]**](GroupReconcileRecord.md) | The list of groups the user was added to due to a reconcile. | [optional] 
**groups_removed_from** | [**[GroupReconcileRecord]**](GroupReconcileRecord.md) | The list of groups the user was removed from due to a reconcile. | [optional] 
**resulting_groups** | [**[GroupReconcileRecord]**](GroupReconcileRecord.md) | The list of groups the user is a member of as a result of reconciliation. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


