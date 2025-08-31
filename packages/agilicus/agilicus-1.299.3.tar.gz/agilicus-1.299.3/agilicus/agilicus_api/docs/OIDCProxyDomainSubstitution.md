# OIDCProxyDomainSubstitution

This object allows users to configure how domain substitution is performed on headers. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**standard_headers** | [**OIDCProxyStandardHeader**](OIDCProxyStandardHeader.md) |  | [optional] 
**other_headers** | [**[OIDCProxyHeaderMapping]**](OIDCProxyHeaderMapping.md) | The list of other headers that need to be substituted. | [optional] 
**path** | **bool** | Configure whether domain substitution acts on the path as well as the host in the uri. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


