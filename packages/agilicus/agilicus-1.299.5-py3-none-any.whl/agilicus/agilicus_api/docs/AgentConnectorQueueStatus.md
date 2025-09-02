# AgentConnectorQueueStatus

Agent connector queue status. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**queue_name** | **str** | The system generated queue name.  | 
**expired** | **bool** | False if the queue exist  True if the queue no longer exists (TTL has expired). The queue will be garbage collected (deleted) if a request to create another queue is made and no the number of queues per connector has been exceeded.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


