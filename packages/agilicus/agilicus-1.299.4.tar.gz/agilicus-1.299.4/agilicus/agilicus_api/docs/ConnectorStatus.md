# ConnectorStatus

Status information pertaining to a Connector

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_services** | [**[ApplicationService]**](ApplicationService.md) | The list of application services associated with this secure agent | [optional] 
**service_account_id** | **str** | Service account user GUID used to deploy the connector | [optional] [readonly] 
**stats** | [**ConnectorStats**](ConnectorStats.md) |  | [optional] 
**num_instances_lifetime** | **int** | Number of ConnectorInstances that have been created for this connector_id lifetime. | [optional] 
**instances** | [**[ConnectorInstance]**](ConnectorInstance.md) | The list of connector instances | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


