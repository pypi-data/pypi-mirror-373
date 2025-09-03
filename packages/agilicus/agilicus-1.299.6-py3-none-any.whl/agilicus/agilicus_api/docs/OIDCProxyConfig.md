# OIDCProxyConfig

The configuration for OIDC-Proxy to set/substitute headers, set domain name mappings, set authentification configurations if auth is enabled and manipulate content based on its type. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**headers** | [**OIDCProxyHeader**](OIDCProxyHeader.md) |  | 
**domain_mapping** | [**OIDCProxyDomainMapping**](OIDCProxyDomainMapping.md) |  | 
**content_manipulation** | [**OIDCProxyContentManipulation**](OIDCProxyContentManipulation.md) |  | 
**auth** | [**OIDCAuthConfig**](OIDCAuthConfig.md) |  | [optional] 
**upstream_config** | [**OIDCProxyUpstreamConfig**](OIDCProxyUpstreamConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


