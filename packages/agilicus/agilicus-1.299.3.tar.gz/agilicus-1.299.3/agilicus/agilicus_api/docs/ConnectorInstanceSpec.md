# ConnectorInstanceSpec

The specification of the ConnectorInstance

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_id** | **str** | Unique identifier | [readonly] 
**org_id** | **str** | Unique identifier | 
**require_instance_service_account** | **bool** | If require_instance_service_account is false (default), the service account in the AgentConnector will be used for this instance. If require_instance_service_account is true , a unique service account for this instance will be created.  | [optional]  if omitted the server will use the default value of False
**service_account_id** | **str** | Service account user GUID used to deploy the connector | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


