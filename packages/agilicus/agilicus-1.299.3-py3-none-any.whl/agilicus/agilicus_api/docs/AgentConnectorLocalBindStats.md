# AgentConnectorLocalBindStats

Statistics of a configured local bind. This will provide the running address of the bind as well as any errors encounred setting it up. If the status is `good`, then the errors occured in the past, and can be ignored. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bind_status** | **str** | The status of the bind. The possible values mean:  - &#x60;good&#x60;: the agent is listening on the the &#x60;running_address&#x60; for connections. - &#x60;warn&#x60;: the agent is listening on the &#x60;running_address&#x60; for connections but something is not   quite right. Check &#x60;recent_errors&#x60; for a hint. - &#x60;down&#x60;: the agent is not listening to an address corresponding  to &#x60;bind_address&#x60;. Check &#x60;recent_errors&#x60;   for the cause.  | 
**running_address** | **str, none_type** | The address and port on which the agent is listening for connections. This takes the form of &#x60;ip:port&#x60;. Note that this may not correspond to a concrete address if the bind address was not set.  | 
**bind_address** | **str** | The address and port configured for this bind. Use this to find the item corresponding to a given AgentConnectorLocalBind.  | 
**recent_errors** | [**[AgentConnectorLocalBindError]**](AgentConnectorLocalBindError.md) | The most recently encountered errors when binding to &#x60;bind_address&#x60;. Note that this list not being empty does not imply that the agent successfully bound: errors prior to the successful bind will still be present in the list. Use the &#x60;bind_status&#x60; instead.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


