# AgentConnectorQueueSpec

An agent connector queue for receiving asynchronous messages. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_id** | **str** | Unique identifier | 
**org_id** | **str** | Unique identifier | 
**instance_name** | **str** | A unique name for a queue within a connector_id.  There is a fixed number of queues permitted for a connector_id.  | 
**queue_ttl** | **int** | Queues will expire after this period of time only when they are not used (e.g. do not have consumers). This value is in seconds. By default, if no value is provided, the system ttl default is set to 3600 (1 hour).  | [optional] 
**dynamic_routes_enabled** | **bool** | Whether or not to receive dynamic route requests  | [optional] 
**on_demand_routes_enabled** | **bool** | Whether or not on demand routes are supported for this tunnel. A tunnel which supports on demand routing will not bring up a tunnel until a request has arrived at the router.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


