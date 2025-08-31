# OIDCProxyUpstreamConfig

The configuration of the upstream host and scheme.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scheme** | **str** | The scheme defines the type of protocol to be used to access the upstream. | 
**hostname** | **str** | The hostname of the upstream server. It will be used to provision the host/authority header for requests the proxy forwards to it. | 
**port** | **int, none_type** | The port on the upstream to access. The port will be inferred as 80 or 443 if unspecified depending on the scheme. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


