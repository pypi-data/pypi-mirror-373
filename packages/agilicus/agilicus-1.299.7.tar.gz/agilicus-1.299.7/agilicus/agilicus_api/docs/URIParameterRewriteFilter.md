# URIParameterRewriteFilter

This object configures more advanced rewrites on a header. It enables the specification of specific uri parameters and encodings to enable richer substitution. This filter expects uris with paramaters that start with a '?', seperated by '&' and are uri-encoded. eg: \"https://my-site.com?redirect=https%3A%2F%2Fmy-site.com\" 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**header** | **str** | The header to rewrite. Case insensitive | 
**parameter** | **str** | The uri parameter to rewrite. | 
**rewrite_type** | **str** | The type of object this is. This is used when an interface expects a OIDCProxyHeaderRewriteFilter.  | defaults to "uriparameterRewrite"
**exact_value** | **str** | The value to find in plaintext. | [optional] 
**exact_rewrite_value** | **str** | The value to replace in plaintext. | [optional] 
**base64** | **bool** | This setting will cause the filter to treat the parameter as base64 encoded and will cause the filter to decode before making the substitution, and reencode after the substitution.  | [optional]  if omitted the server will use the default value of False
**deflate** | **bool** | This setting will cause the filter to treat the parameter as deflated. This will cause the filter to inflate the paramater before the substitution is made, and deflate after the substitution.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


