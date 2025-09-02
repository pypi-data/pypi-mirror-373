# BulkDeleteLabelledObjectsRequest

Requests deletion of many LabelledObjects. This is typically used to clean up when an object has been deleted. Note that it is not an error to delete nothing in response to this. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**object_ids** | **[str]** | The IDs of objects to clean up. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


