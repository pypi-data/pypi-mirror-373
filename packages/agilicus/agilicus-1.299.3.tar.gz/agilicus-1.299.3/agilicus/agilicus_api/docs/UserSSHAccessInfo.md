# UserSSHAccessInfo

A UserSSHAccessInfo describes whether a user has access to a machine via ssh as well as various bits of metadata related to the machine to help users navigate to it. If a user has access to a machine, querying for that user will return information related to that machine. If a ssh machine is public that machone will also appear here. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**UserSSHAccessInfoStatus**](UserSSHAccessInfoStatus.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


