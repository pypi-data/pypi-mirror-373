# AgentConnectorSpecificStats

Statistics periodically collected from a running AgentConnector. These statistics may be used to understand how the AgentConnector is performing, diagnose issues, and so on. Note that upstream_stats may not be available unless a user has requested publication of them 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**system** | [**AgentConnectorSystemStats**](AgentConnectorSystemStats.md) |  | 
**transport** | [**AgentConnectorTransportStats**](AgentConnectorTransportStats.md) |  | 
**shares** | [**AgentConnectorShareStats**](AgentConnectorShareStats.md) |  | [optional] 
**authz** | [**AgentConnectorAuthzStats**](AgentConnectorAuthzStats.md) |  | [optional] 
**proxy** | [**AgentConnectorProxyStats**](AgentConnectorProxyStats.md) |  | [optional] 
**user** | [**AgentConnectorUserStats**](AgentConnectorUserStats.md) |  | [optional] 
**application_stats** | [**ApplicationStatsList**](ApplicationStatsList.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


