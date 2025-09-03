# AgentConnectorSpec

The specification of the Connector

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A descriptive name for the connector | 
**org_id** | **str** | Unique identifier | 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**max_number_connections** | **int** | The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connector is effectively unused by this Secure Agent.  | [optional] 
**connection_uri** | **str** | Overrides the default URI used to connect to this connector. This can be used to point the Secure Agent somewhere other than the default.  | [optional] 
**service_account_required** | **bool** | If service_account_enabled field is set to true, a service account will be created. If service_account_enabled field is set to false, the service account will be deleted. If the service_account_enabled field is not set no action on the service account is taken.  | [optional] 
**local_authentication_enabled** | **bool** | Determines whether or not the agent will expose an endpoint for local authentication | [optional] 
**proxy_tunnel_termination** | **str** | How a proxy tunnel is terminated.   - tcp: terminate the tunnel at a TCP socket   - inproc: terminate the tunnel at an inprocess socket Note: if not specified, the connector will choose, likely based on its version.  | [optional] 
**provisioning** | [**AgentConnectorSpecProvisioning**](AgentConnectorSpecProvisioning.md) |  | [optional] 
**routing** | [**AgentConnectorCloudRouting**](AgentConnectorCloudRouting.md) |  | [optional] 
**connector_cloud_routing** | [**ConnectorCloudRouting**](ConnectorCloudRouting.md) |  | [optional] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**revocation_proxy** | [**CertificateRevocationProxy**](CertificateRevocationProxy.md) |  | [optional] 
**egress_gateway** | [**EgressGateway**](EgressGateway.md) |  | [optional] 
**demo** | **bool** | When true, the connector is considered a demo connector, and will be auto-deleted after 24 hours.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


