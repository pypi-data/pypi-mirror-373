# UserApplicationAccessInfo

A UserApplicationAccessInfo describes whether a user has access to an application as well as various bits of metadata related to the application to help users navigate to it. If a user has access to an instance of an application, querying for that user will return information related to that instance in the record set. If an application is public, then a record will also appear of that application. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**UserApplicationAccessInfoStatus**](UserApplicationAccessInfoStatus.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


