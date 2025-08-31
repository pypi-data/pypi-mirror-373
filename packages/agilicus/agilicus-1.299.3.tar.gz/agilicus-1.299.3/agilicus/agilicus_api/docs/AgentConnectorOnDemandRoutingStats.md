# AgentConnectorOnDemandRoutingStats

Statistics related to the agent's on demand routing functionality. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**queue_full** | **int** | The number of route requests dropped because the request processing queue was full. This incrementing could indicate that a large number of requests hit a connector that just came up all at once, or that the connector is running on a slow system.  | 
**request_expired** | **int** | The number of route requests dropped because it was too old. This typically happens when the connector has been down for a long time, but it could also happen if the system is overloaded. It could also happen if there is a time sync problem between the connector and the cloud infrastructure.  | 
**tunnel_already_exists** | **int** | The number of route requests which were ignored because a tunnel for the route already existed. This typically happens due to a race where many concurrent requests satisfied by the same tunnel come in to the system.  | 
**unused_pop** | **int** | The number of route requests from a pop to which this connected is not configured to connect.  | 
**target_number_on_demand_connections** | **int** | The number of on demand connections which should be in an active state. Note that this may be less than active_connections if the AgentConnector is currently applying configuration changes. It may be more than active_connections if there is a connectivity issue, or connections are first starting. This is included in the overall target_number_connections, but broken out for diagnostics purposes.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


