# ConnectorSystemStats

System stats common to all connectors 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**os_version** | **str** | The version of the operating system on which the Connector is running. | [optional] 
**os_uptime** | **int** | The length of time, in seconds, the operating system has been running. | [optional] 
**hostname** | **str** | The hostname of the computer on which the Connector is running. | [optional] 
**version** | **str** | The version of software currently running for this Connector. This includes both the version number and the commit reference from which it was built.  | [optional] 
**config_update_time** | **datetime** | The date-time when the connector last updated its running configuration from the API.  | [optional] 
**connector_instance_id** | **str** | The connector_instance_id (if applicable).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


