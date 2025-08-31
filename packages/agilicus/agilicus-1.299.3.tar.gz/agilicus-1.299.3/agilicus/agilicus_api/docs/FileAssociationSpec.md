# FileAssociationSpec

The details of a file association. Which object it is associated with, which org, etc. The file_id represents the file to be associated. The object_id represents the object to be associated. The org_id represents the organisation owning the object.  Only objects owned by an organisation with permission to modify the file may create an association. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** | Unique identifier | 
**object_id** | **str** | Unique identifier | 
**org_id** | **str** | Unique identifier | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


