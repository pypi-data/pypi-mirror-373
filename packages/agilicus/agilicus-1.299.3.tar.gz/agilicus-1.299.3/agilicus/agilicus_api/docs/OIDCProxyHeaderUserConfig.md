# OIDCProxyHeaderUserConfig

The configuration for users to set header value, add header fields and remove existing header fields. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**set** | [**[OIDCProxyHeaderMapping]**](OIDCProxyHeaderMapping.md) | The list of existing headers that will be set to new values. | [optional] 
**add** | [**[OIDCProxyHeaderMapping]**](OIDCProxyHeaderMapping.md) | The list of headers (name and value) that will be added. | [optional] 
**remove** | [**[OIDCProxyHeaderName]**](OIDCProxyHeaderName.md) | The list of header names that will be removed. | [optional] 
**remove_match** | [**[OIDCProxyHeaderMatch]**](OIDCProxyHeaderMatch.md) | The list of headers that will be removed. If multiple values for the header are present, only the matching ones will be removed. If after removal, the header is empty, it will be removed entirely.  | [optional] 
**filters** | [**[OIDCProxyHeaderRewriteFilter]**](OIDCProxyHeaderRewriteFilter.md) | A list of additional mapping filters to be applied | [optional]  if omitted the server will use the default value of []
**replace** | [**[OIDCProxyHeaderReplace]**](OIDCProxyHeaderReplace.md) | The list of header names that will be replaced. If header does not match, it will not be replaced with the new header  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


