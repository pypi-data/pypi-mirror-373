# UpstreamAliasSpec

The upstream alias spec defines how the aliasing works. A mapping of upstream identity provider to a list of aliases is defined for a specific client id. Each alias will be displayed to the user when authenticating against that client id instead of displaying the `aliased` upstream 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | ID of the organisation which owns the issuer | 
**client_id** | **str** | The client id that the aliasing applies to | 
**aliases** | [**[UpstreamAliasMapping]**](UpstreamAliasMapping.md) | A list of aliases that are applied for the specified client_id | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


