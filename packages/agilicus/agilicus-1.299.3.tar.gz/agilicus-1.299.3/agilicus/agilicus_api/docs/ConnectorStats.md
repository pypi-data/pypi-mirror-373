# ConnectorStats

Statistics periodically collected from a running Connector. These statistics may be used to understand how the Connector is performing, diagnose issues, and so on. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**ConnectorStatsMetadata**](ConnectorStatsMetadata.md) |  | 
**overall_status** | **str** | The summary status of the Connector. - A &#x60;good&#x60; status means that no action is neccessary on this Connector - A &#x60;warn&#x60; status means that there is an issue that should be dealt with   Examples include connections restarting frequently. - A &#x60;down&#x60; status indicates that there is a service accessibility problem   that should be dealt with as soon as possible. This could mean that there is a   problem with the Connector&#39;s configuration, or the platform. - A &#x60;stale&#x60; status indicates that although there may not be anything wrong,   we haven&#39;t been able to update the status recently. This may indicate   a communications issue between Agilicus and the Connector.  | 
**overall_status_info** | **[str]** | A list of strings that provide more info to further identify the reason for a particular overall_status. For example, if the overall_status is &#x60;warn&#x60;, an entry in this array would provide more details as to its reason.  | [optional] 
**forwarder_stats** | [**ServiceForwarderStatsGroup**](ServiceForwarderStatsGroup.md) |  | [optional] 
**app_service_stats** | [**ApplicationServiceStatsGroup**](ApplicationServiceStatsGroup.md) |  | [optional] 
**share_service_stats** | [**FileShareServiceStatsGroup**](FileShareServiceStatsGroup.md) |  | [optional] 
**diagnostic_stats** | [**ConnectorDiagnosticStats**](ConnectorDiagnosticStats.md) |  | [optional] 
**system** | [**ConnectorSystemStats**](ConnectorSystemStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


