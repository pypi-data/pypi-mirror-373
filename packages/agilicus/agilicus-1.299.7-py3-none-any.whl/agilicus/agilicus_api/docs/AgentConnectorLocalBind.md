# AgentConnectorLocalBind

Configures the agent to bind to an address so that it my serve requests on it. Note that if the bind fails, the agent will try to bind again in a short period of time. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bind_host** | **str, none_type** | The host or IP address to bind to. &#x60;0.0.0.0&#x60; will bind to all IPv4 addresses. &#x60;::&#x60; will bind to all IPv6 addresses. If set to null this will bind to locally available unicast and anycast IP addresses. Setting it to a hostname will cause the agent to bind to the IP of that host.  | 
**bind_port** | **int** | The port to bind to. 0 binds to a random, free port chosen by the system. Be careful to choose a port that the agent has permission to bind. E.g. on some systems, low-numbered ports such as 443 require special permissions.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


