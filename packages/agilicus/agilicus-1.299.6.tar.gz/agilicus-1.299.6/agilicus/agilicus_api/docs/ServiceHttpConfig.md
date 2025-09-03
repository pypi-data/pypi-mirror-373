# ServiceHttpConfig

HTTP configuration for an Application Service providing connectivity to an HTTP endpoint. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**disable_http2** | **bool** | Normally the proxy announces HTTP/2 capability. Allow this to be disabled if required by the service or clients.  The default behavior is always announce HTTP/2 support.  | [optional]  if omitted the server will use the default value of False
**js_injections** | [**[JSInject]**](JSInject.md) |  | [optional] 
**set_token_cookie** | **bool** | This service requires its cookie to be set.  | [optional]  if omitted the server will use the default value of False
**rewrite_hostname** | **bool** | When proxying HTTP requests to the upstream, rewrite the host header to the hostname configured for this Service.  | [optional] 
**rewrite_hostname_with_port** | **bool** | When proxying HTTP requests to the upstream, include the port from this service in the host header. If this field is True, but rewrite_hostname False, this property is assumed to be False.  | [optional] 
**rewrite_hostname_override** | **str** | When proxying HTTP requests to the upstream, rewrite the host header to this value. This property will override the hostname and will assume rewrite_hostname is False.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


