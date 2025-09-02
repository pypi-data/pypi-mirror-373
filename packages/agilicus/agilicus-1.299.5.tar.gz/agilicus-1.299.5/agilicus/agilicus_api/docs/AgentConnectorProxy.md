# AgentConnectorProxy

Handles the configuration of a connector (called the outer connector) providing a proxy to another connector (called the inner connector).  This is useful where the inner connector may not have direct access to the internet (behind a DMZ, or Virtually Air gaped), whereas another connector (the outer connector) has direct internet access.  On creation of this object, if local_bind is not defined, the following default will be created:   local_port: 18443   local_bind.bind_host: 0.0.0.0 The local_bind refers to the coordinates of the proxy located in the outer_connector_id. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**AgentConnectorProxySpec**](AgentConnectorProxySpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**AgentConnectorProxyStatus**](AgentConnectorProxyStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


