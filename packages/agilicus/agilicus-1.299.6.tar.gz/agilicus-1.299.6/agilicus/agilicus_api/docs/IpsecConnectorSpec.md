# IpsecConnectorSpec

An IPsec Connector Specification.  The configuration of a connector uses an inheritance model so that connections within a connector can re-use the common configuration of the connector.  Should a specific connection require overriding specific attributes of the connection, each connection has its own config section that allows this override.  Each connection has a name that must be configured to instantiate a connection. A connection can be created by a PUT to the connector endpoint. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the IPsec connector  | 
**org_id** | **str** | Unique identifier | 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**ipsec_gateway_id** | **str** | The GUID of the IpsecGateway where this connector is instantiated from. | [optional] 
**connections** | [**[IpsecConnection]**](IpsecConnection.md) | Defines the set of IPsec connections within the connector. Adding an IpsecConnection(s) here will instantiate the connection(s). Removing an IpsecConnection(s) here cause the connection(s) to be torn down.  | [optional] 
**connector_cloud_routing** | [**ConnectorCloudRouting**](ConnectorCloudRouting.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


