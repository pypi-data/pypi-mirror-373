# ManagedUpstreamIdentityProvider

Managed upstream identity provider

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the managed upstream identity provider. Ex google | [readonly] 
**enabled** | **bool** | Describes whether the managed upstream identity provider is enabled | defaults to False
**prompt_select_account** | **bool** | Shows the user an account selector, negating silent single sign on, but allowing the user to pick which account they intend to sign in with, without requiring credential entry. The support of this feature is dependent on the upstream provider.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


