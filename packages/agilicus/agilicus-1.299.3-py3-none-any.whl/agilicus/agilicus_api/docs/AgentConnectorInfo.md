# AgentConnectorInfo

Information pertaining to a Connector

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**local_authentication_enabled** | **bool** | Determines whether or not the agent will expose an endpoint for local authentication | [optional] 
**connections_info** | [**[AgentConnectorConnectionInfo]**](AgentConnectorConnectionInfo.md) | The list of connections associated with this agent | [optional] 
**allow_list** | [**AllowMapCompiled**](AllowMapCompiled.md) |  | [optional] 
**extended_rule_map** | **{str: ([RuleConfig],)}** | A map of hostname lookup to RuleConfig  | [optional] 
**authz_public_key** | **str** | The PEM encoded public key used for validating bearer tokens | [optional] 
**application_service_uri** | **str** | The URI this connector will establish as the destination URI for service forwarder requests. An agent would request a certificate for the hostname provided as part of the URI for other connectors to establish a TLS connection to this connector.  | [optional] 
**tunnel_uri** | **str** | The URI this connector uses to establish its tunnels. | [optional] 
**proxy_tunnel_termination** | **str** | How a proxy tunnel is terminated.   - tcp: terminate the tunnel at a TCP socket   - inproc: terminate the tunnel at an inprocess socket Note: if not specified, the connector will choose, likely based on its version.  | [optional] 
**service_forwarders** | [**[ServiceForwarder]**](ServiceForwarder.md) | The list of service forwarders associated with this connector. | [optional] 
**from_service_forwarders** | [**[ServiceForwarder]**](ServiceForwarder.md) | The list of service forwarders that are forwarded to this connector. | [optional] 
**routing** | [**AgentConnectorCloudRouting**](AgentConnectorCloudRouting.md) |  | [optional] 
**tunnel_info** | [**AgentConnectorTunnelInfo**](AgentConnectorTunnelInfo.md) |  | [optional] 
**active_transfers** | [**[ConnectorSecureTransfer]**](ConnectorSecureTransfer.md) | secure transfers that are in progress for the connector. | [optional] 
**stats_publishing** | [**StatsPublishingConnectorConfig**](StatsPublishingConnectorConfig.md) |  | [optional] 
**revocation_proxy** | [**CertificateRevocationProxy**](CertificateRevocationProxy.md) |  | [optional] 
**egress_gateway** | [**EgressGateway**](EgressGateway.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


