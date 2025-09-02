# UpstreamAliasMapping

An issuer alias object specifies what upstream providers are an alias to a given upstream provider. An upstream provider should be specified once per client, duplicate entries will be rejected. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upstream_provider_name** | **str** | A name used to uniquely refer to the upstream identity provider that is being aliased | 
**aliased_upstream_provider_names** | **[str]** | The list of upstream providers that are aliasing the upstream provider specified by &#x60;upstream_provider_name&#x60; | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


