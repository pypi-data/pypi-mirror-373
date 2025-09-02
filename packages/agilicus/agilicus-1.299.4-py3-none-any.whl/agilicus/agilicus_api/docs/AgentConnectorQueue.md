# AgentConnectorQueue

An agent connector queue for receiving messages on a particular topic.  Connector queues have a finite lifetime (TTL). The default ttl is system generated at 3600 seconds.  The system allows a predefined set of queues for connector_id (10).  Unused queues (once they are expired), will be garbaged collected (deleted) so that new queues can be allocated by future consumers. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**AgentConnectorQueueSpec**](AgentConnectorQueueSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**AgentConnectorQueueStatus**](AgentConnectorQueueStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


