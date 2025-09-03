# AgentConnectorRoutingStats

Statistics related to how the agent routes requests. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**local_bindings** | [**[AgentConnectorLocalBindStats]**](AgentConnectorLocalBindStats.md) | The status of the addresses to which the agent is configured to bind. This will show the running address of the bind if a hostname or random port was chosen. It can also help to diagnose problems with binding.  | 
**on_demand** | [**AgentConnectorOnDemandRoutingStats**](AgentConnectorOnDemandRoutingStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


