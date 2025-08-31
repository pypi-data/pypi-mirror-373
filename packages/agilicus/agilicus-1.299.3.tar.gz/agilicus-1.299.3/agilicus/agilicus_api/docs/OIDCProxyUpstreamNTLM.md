# OIDCProxyUpstreamNTLM

Configures the proxy to pass through NTLM authentication. If enabled, the proxy will forward challenges to the client. It will further ensure that challenge responses and further requests from the same downstream connection are sent through the same upstream connection. That is, if this mode is enabled, the proxy will ensure a one to one mapping of downstream connection to upstream connection. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ntlm_passthrough** | **bool** | Enables NTLM passthrough | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


