# ObjectCredentialSpec

The specification of the object credentials. The object_id and object_type link the credential to an object in the system. The purpose describes how the credential is used, and the priority indicates from high to low which credential should be used first, if a given object has multiple. Only a single ObjectCredential can exist for a given (object_id, object_type, purpose, priority, org_id) combination. Note that once set, 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object_id** | **str** | Unique identifier | 
**object_type** | [**ObjectType**](ObjectType.md) |  | 
**purpose** | [**CredentialPurpose**](CredentialPurpose.md) |  | 
**priority** | **int** | The priority of the credential. Higher priorities are used first.  | 
**org_id** | **str** | Unique identifier | [optional] 
**secrets** | [**ObjectCredentialSecrets**](ObjectCredentialSecrets.md) |  | [optional] 
**description** | **str** | A short description of the secret. E.g. what it applies to, how long it&#39;s good for and so on.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


