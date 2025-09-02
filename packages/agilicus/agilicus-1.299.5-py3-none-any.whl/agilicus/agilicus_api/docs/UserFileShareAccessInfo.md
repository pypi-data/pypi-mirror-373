# UserFileShareAccessInfo

A UserFileShareAccessInfo describes whether a user has access to a file share as well as various bits of metadata related to the file share to help users navigate to it. If a user has access to an instance of a file share, querying for that user will return information related to that instance in the record set. If a file share is public, then a record will also appear for that file share. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**UserFileShareAccessInfoStatus**](UserFileShareAccessInfoStatus.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


