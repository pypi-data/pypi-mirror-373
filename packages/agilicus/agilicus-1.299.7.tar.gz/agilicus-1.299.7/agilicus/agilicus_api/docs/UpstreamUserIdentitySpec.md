# UpstreamUserIdentitySpec

The specification of a user's upstream identity. This contains the information that uniquely identifies the user in a given upstream identity provider. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upstream_user_id** | **str** | The unique id of the user in the upstream identifier provider. This need not be globally unique within the system. However, the pair of it and &#x60;upstream_idp_id&#x60; must be.  | 
**upstream_idp_id** | **str** | The unique id of the upstream identity provider within the system. When the user authenticates using the corresponding upstream identity provider, they will join against the user record owning this &#x60;UpstreamUseridentitySpec&#x60; by linking with the &#x60;upstream_user_id&#x60; as given by the upstream identity. Typically this will be the issuer URI. Note that it is case sensitive.  | 
**local_user_id** | **str** | The unique id of the user within the system. This is the user to which this identity is tied.  | 
**attributes** | [**UserAttributes**](UserAttributes.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


