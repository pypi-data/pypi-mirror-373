# ClearFileAssociationRequest

Requests that a set of associations be cleared. Every affected File will be marked as pending_delete if it has no remaining associations after clearing.  The request will search for all associations with the provided parameters, deleting them. `object_id` restricts the search to only those associations linked to the object_id. `org_id` restricts the search to only those associations owned by org_id.  Note that any deleted files will continue to exist: both the API object and the storage. However, a garbage collection task may choose to remove the storage at some point.  If object_id is undefined, then all associations for an organisation will be cleaned. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**object_id** | **str** | Unique identifier | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


