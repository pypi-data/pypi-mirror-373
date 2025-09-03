# StatsPublishingLevelConfig

Configures for how long to publish statistics at a given level. The connector will publish statistics from when it receives this request until at least the amount of time configured here has elapsed. Note that multiple calls to this will possibly increase how long the connector publishes for, but will not reduce that time. If a particular level's duration is omitted, existing publishing config of that level will not be modified: if already publishing, the connector will continue until it times out. If not publishing, it will not begin. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary_duration_seconds** | **int** | For how long to publish summary statistics. | [optional] 
**detailed_duration_seconds** | **int** | For how long to publish detailed statistics. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


