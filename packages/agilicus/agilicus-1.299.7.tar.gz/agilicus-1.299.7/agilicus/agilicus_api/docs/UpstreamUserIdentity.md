# UpstreamUserIdentity

A user's identity in an upstream identity provider. A user in the system may be tied to multiple upstream sources of identity. For example, the user may have both a google account and a github account. They can link these accounts by tying the upstream identities to the identity of the user in this system. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**UpstreamUserIdentitySpec**](UpstreamUserIdentitySpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


