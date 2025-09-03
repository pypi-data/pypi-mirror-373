# ConnectorSpec

The specification of the Connector

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A descriptive name for the connector | 
**org_id** | **str** | Unique identifier | 
**connector_type** | **str** | The type of the connector | 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**service_account_id** | **str** | Service account user GUID used to deploy the connector | [optional] [readonly] 
**connector_cloud_routing** | [**ConnectorCloudRouting**](ConnectorCloudRouting.md) |  | [optional] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**demo** | **bool** | When true, the connector is considered a demo connector, and will be auto-deleted after 24 hours.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


