# ApplicationServiceCommonStats

The common statistics for an application service. Depending on how the connector routes to the application service, and the level of stats being published, it mave have any combination of network, http, share, summary or detailed. For example, a network only reached by wscat forwarding will not have `http_*_stats`. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**network_summary_stats** | [**NetworkSummaryStats**](NetworkSummaryStats.md) |  | [optional] 
**http_summary_stats** | [**HTTPSummaryStats**](HTTPSummaryStats.md) |  | [optional] 
**network_detailed_stats** | [**NetworkDetailedStats**](NetworkDetailedStats.md) |  | [optional] 
**http_detailed_stats** | [**HTTPDetailedStats**](HTTPDetailedStats.md) |  | [optional] 
**share_summary_stats** | [**ShareSummaryStats**](ShareSummaryStats.md) |  | [optional] 
**share_detailed_stats** | [**ShareDetailedStats**](ShareDetailedStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


