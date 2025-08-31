# AgentConnectorCloudRouting

Configures how an agent exposes resources through itself. For example, configure the local addresses on which the agent will listen for requests for the resources assigned to it. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**local_binds** | [**[AgentConnectorLocalBind]**](AgentConnectorLocalBind.md) | A list describing how to expose resources locally (e.g. not via a tunnel). Each item in this list will configure the agent to bind to a TCP address so that it may serve requests.  | 
**tunneling** | [**AgentConnectorTunneling**](AgentConnectorTunneling.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


