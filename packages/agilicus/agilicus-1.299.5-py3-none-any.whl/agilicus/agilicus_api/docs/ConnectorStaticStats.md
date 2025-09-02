# ConnectorStaticStats

The last reported statistics for a connector, broken down by instance, along with the overall status of the connector. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_id** | **str** | Unique identifier | 
**instances** | [**[ConnectorInstance]**](ConnectorInstance.md) | Basic information about the connector&#39;s instances and their status  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


