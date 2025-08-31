# UserRequestInfo

The user request information describes a user's request. A request can be anything that requires an admin to grant permission to the user for access to a resource. For example if a user required access to an application called `app` they could request access via this mechanism. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**UserRequestInfoSpec**](UserRequestInfoSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**UserRequestInfoStatus**](UserRequestInfoStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


