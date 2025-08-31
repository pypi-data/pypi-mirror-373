# AgentConnectorStatus

Status information pertaining to a Connector. Note that stats will only be returned if explicitly requested. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_services** | [**[ApplicationService]**](ApplicationService.md) | The list of application services associated with this agent | [optional] 
**service_account_id** | **str** | Service account user GUID used to deploy the connector | [optional] 
**num_instances_lifetime** | **int** | Number of AgentConnectorInstances that have been created for this connector_id lifetime. | [optional] 
**info** | [**AgentConnectorInfo**](AgentConnectorInfo.md) |  | [optional] 
**stats** | [**AgentConnectorStats**](AgentConnectorStats.md) |  | [optional] 
**local_authentication** | [**AgentLocalAuthInfo**](AgentLocalAuthInfo.md) |  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**stats_publishing** | [**StatsPublishingConnectorConfig**](StatsPublishingConnectorConfig.md) |  | [optional] 
**egress_gateway** | [**EgressGateway**](EgressGateway.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


