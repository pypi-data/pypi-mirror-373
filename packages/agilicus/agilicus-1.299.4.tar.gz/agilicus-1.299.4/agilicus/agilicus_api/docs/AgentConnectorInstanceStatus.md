# AgentConnectorInstanceStatus

Status information pertaining to a Connector. Note that stats will only be returned if explicitly requested. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The agent connector instance name. | [optional] 
**instance_number** | **int** | The agent connector instance number. | [optional] 
**service_account_id** | **str** | Service account user GUID used to deploy the connector | [optional] 
**stats** | [**AgentConnectorStats**](AgentConnectorStats.md) |  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**sys_info** | [**AgentConnectorSystemInfo**](AgentConnectorSystemInfo.md) |  | [optional] 
**perf_metrics** | [**AgentConnectorPerformanceMetrics**](AgentConnectorPerformanceMetrics.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


