# ObjectCredential

Credentials associated with an object in the system. Depending on the type of object, these may be used for different purposes: presenting credentials to an upstream service so that the end user does not have to; authenticating an upstream connection using mTLS, etc. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**ObjectCredentialSpec**](ObjectCredentialSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**ObjectCredentialStatus**](ObjectCredentialStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


