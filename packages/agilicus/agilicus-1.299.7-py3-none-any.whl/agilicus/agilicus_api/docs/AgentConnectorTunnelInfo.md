# AgentConnectorTunnelInfo

Modifies the default behaviour of how an agent connector exposes its tunnels. For example, this allows the agent to route TCP tunnels using hostnames which only resolve on the network in which it is installed. Note that the agent connector will typically only route on these hostnames if a LocalBind has been configured. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hosts** | **[str], none_type** | A list of domain names the agent will listen to for routing tunnels. Typically these will be a hosts which resolve locally within the network for short-circuting purposes.  | 
**pop_domains** | **[str], none_type** | A list of point of presence routers to which the connector will establish tunnels.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


