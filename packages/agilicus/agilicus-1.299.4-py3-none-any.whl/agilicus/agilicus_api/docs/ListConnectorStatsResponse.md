# ListConnectorStatsResponse

The result of querying for many connectors' stats. This will hold an item for each matching connector's stats. Note that if a connector does not exist, or its states were not up to date, it will not have an entry in the corresponding array. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dynamic_stats** | [**[AgentConnectorDynamicStats]**](AgentConnectorDynamicStats.md) |  | [optional] 
**static_stats** | [**[ConnectorStaticStats]**](ConnectorStaticStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


