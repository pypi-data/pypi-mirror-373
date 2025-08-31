# ConnectorStatsMetadata

Information about an ConnectorStats object. Useful to understand when stats were published or updated. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collection_time** | **datetime** | When the statistics were collected | 
**creation_time** | **datetime** | When the statistics were first created | [optional] [readonly] 
**receipt_time** | **datetime** | When the statistics were received for storage | [optional] [readonly] 
**connector_id** | **str** | The identifier of the Connector publishing these statistics. The Connector publishes this information in order to ensure that an Connector does not accidentally publish to the wrong endpoint.  | [optional] 
**connector_org_id** | **str** | The organisation identifier of the Connector publishing these statistics. The Connector publishes this information in order to ensure that an Connector does not accidentally publish to the wrong endpoint.  | [optional] 
**connector_instance_id** | **str** | The connector_instance_id (if applicable).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


