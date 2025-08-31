# PerInstanceUpstreamStats

Upstream statistics for a given ApplicationService as seen by an AgentConnector instance. The set of statistics available for it depend on the concrete type of the ApplicationService as well as the stats publishing configuration. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_instance_id** | **str** | Unique identifier | 
**upstream_stats** | [**ApplicationServiceCommonStats**](ApplicationServiceCommonStats.md) |  | 
**application_service_id** | **str** | Unique identifier | [optional] 
**application_service_type** | **str** | The type of application service which reported this stat  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


