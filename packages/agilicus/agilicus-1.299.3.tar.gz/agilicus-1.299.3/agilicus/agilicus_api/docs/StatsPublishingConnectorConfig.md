# StatsPublishingConnectorConfig

Configuration for how a connector publishes its statistics. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upstream_network_publishing** | [**StatsPublishingConnectorTypeConfig**](StatsPublishingConnectorTypeConfig.md) |  | 
**upstream_http_publishing** | [**StatsPublishingConnectorTypeConfig**](StatsPublishingConnectorTypeConfig.md) |  | 
**publish_period_seconds** | **int** | How frequently to publish statistics, in seconds. The connector will publish statistics on the provided interval until &#x60;publish_until&#x60;.  | 
**upstream_share_publishing** | [**StatsPublishingConnectorTypeConfig**](StatsPublishingConnectorTypeConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


