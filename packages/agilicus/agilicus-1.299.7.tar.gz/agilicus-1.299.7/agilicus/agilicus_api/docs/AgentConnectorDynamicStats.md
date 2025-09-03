# AgentConnectorDynamicStats

The last reported dynamic stastics for a connector, summarised and broken down by type and instance. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upstream_totals** | [**ApplicationServiceCommonStats**](ApplicationServiceCommonStats.md) |  | 
**metadata** | [**ResourceStatsMetadata**](ResourceStatsMetadata.md) |  | 
**connector_id** | **str** | Unique identifier | [optional] 
**upstream_breakdown** | [**[PerInstanceUpstreamStats]**](PerInstanceUpstreamStats.md) | The breakdown of the upstream statitics. Each item in the array represents the statistics for an ApplicationService as exposed by an instance. Each application service will have an entry for each instance. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


