# AgentConnectorTunneling

Configuration for how agent connectors establish and run their tunnels. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dynamic_routes_enabled** | **bool, none_type** | Whether or not agent-connect dynamic routes are enabled. If true, then the routes are enabled for any routers which support them. If false, then they are disabled for the entire connector. If null or omitted, then they will fall back on the system default.  | [optional] 
**on_demand_routes_enabled** | **bool, none_type** | Whether or not agent-connect on demand routes are enabled. If true, then the connector will only establish tunnels (and their routes) when a router has requested one. If false, then the connector will establish tunnels to all points of presence to which it is associated. If null or omitted, then they will fall back on the system default.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


