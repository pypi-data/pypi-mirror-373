# StatsPublishingConfig

Configures how a connector publishes its statistics. You can control the level of statistics the connector will publish on a per-type basis. Each type supports different levels of publishing (e.g. summary vs detailed). Each level for a type may be configured to publish for a given duration. Typically if you need only one type of stats, you would configure for how long the connector should publish for that type and the desired subtype/level of detail. Continue to submit this configuration until you no longer need the statistics. Note that the connector will stop publishing statistics eventually to avoid unnecessarily consuming bandwidth unless you continue to submit configuration. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upstream_network_publishing** | [**StatsPublishingLevelConfig**](StatsPublishingLevelConfig.md) |  | 
**upstream_http_publishing** | [**StatsPublishingLevelConfig**](StatsPublishingLevelConfig.md) |  | 
**publish_period_seconds** | **int** | How frequently to publish detailed statistics, in seconds. The connector will publish statistics on the provided interval until it has been publishing for &#x60;publish_for_seconds&#x60;.  | 
**upstream_share_publishing** | [**StatsPublishingLevelConfig**](StatsPublishingLevelConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


