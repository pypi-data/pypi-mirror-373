# AgentConnectorDynamicStatsPublish

Published statistics for an agent connector instance. Depending on configuration, different set of statistics will be published. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_instance_id** | **str** | Unique identifier | 
**collection_time** | **datetime** | When the statistics were collected | 
**upstream_stats** | [**ConnectorUpstreamStatsPublish**](ConnectorUpstreamStatsPublish.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


