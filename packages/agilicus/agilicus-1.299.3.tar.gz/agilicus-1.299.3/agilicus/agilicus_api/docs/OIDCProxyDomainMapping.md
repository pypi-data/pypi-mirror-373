# OIDCProxyDomainMapping

The mappings between internal domain names and external domain names.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**primary_external_name** | **str** | The primary external name is the name that gets exposed publicly. | 
**primary_internal_name** | **str** | The primary internal name is the name that used internally in the local environment. | 
**use_service_hostname** | **bool** | The upstream mapped host will be rewritten using the service hostname. If primary_internal_name is not empty, primary_internal_name will take precedence. The service port will be appended to the host if the port is a non-standard port (ie. not 443 or 80)  | [optional] 
**use_recursive_replacement_system** | **bool** | The recurssive replacement system will replace the same domain multiple times if one is a subdomain of the other. In some cases the replacements were designed with the older this type of replacement in mind. In those cases this value should be set to true, otherwise it should be left default (false).  | [optional]  if omitted the server will use the default value of False
**other_mappings** | [**[OIDCProxyDomainNameMapping]**](OIDCProxyDomainNameMapping.md) | The list of extra mappings between internal and external domain names. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


