# OIDCProxyStandardHeader

Standard headers are headers that can be substituted without user's configurations unless specified. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | **bool** | If the location flag is set to true, the location field will be automatically rewritten. | [optional]  if omitted the server will use the default value of True
**origin** | **bool** | If the origin flag is set to true, the origin field will be automatically rewritten. | [optional]  if omitted the server will use the default value of True
**host** | **bool** | If the host flag is set to true, the host field will be automatically rewritten. | [optional]  if omitted the server will use the default value of True
**set_cookie_header** | **bool** | If the set_cookie is set to true, the set_cookie header will be automatically rewritten.  | [optional] 
**cookie** | **bool** | If the cookie is set to true, the cookie header will be automatically rewritten. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


