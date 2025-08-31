# DesktopResourceStats

Stats for a DesktopResource, including basic resource stats. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_id** | **str** | The unique ID of the resource. The id is provided here so that a list of resource stats can be POSTed in a single request.  | [optional] 
**metadata** | [**ResourceStatsMetadata**](ResourceStatsMetadata.md) |  | [optional] 
**overall_status** | **str** | The summary status of the Resource. - A &#x60;good&#x60; status means that no action is neccessary on this Resource - A &#x60;warn&#x60; status means that there is an issue that should be dealt with   Examples include a forwarder resource that cannot bind to the provisioned port (eg. permission   issue binding to port 80) - A &#x60;down&#x60; status indicates that there is a service accessibility problem   that should be dealt with as soon as possible. This could mean that there is a   problem with the Resource&#39;s configuration, or the platform. - A &#x60;stale&#x60; status indicates that although there may not be anything wrong,   we haven&#39;t been able to update the status recently. This may indicate   a communications issue between Agilicus and the Connector containing the resource.  | [optional] 
**last_warning_message** | **str** | A message pertaining to the last warning associated with the resource. This message is persistent in that it will remain when the status goes to &#x60;good&#x60;.  | [optional] 
**session_stats** | [**ResourceSessionStats**](ResourceSessionStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


