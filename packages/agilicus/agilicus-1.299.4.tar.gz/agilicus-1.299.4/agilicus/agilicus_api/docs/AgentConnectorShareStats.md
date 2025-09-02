# AgentConnectorShareStats

Statistics related to Shares exposed by the AgentConnector. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exposed_shares_count** | **int** | The total number of shares currently exposed. | 
**server_running** | **bool** | Whether the server exposing shares is running. | 
**server_start_count** | **int** | The total number of times the share server has started | 
**server_stop_count** | **int** | The total number of times the share server has stopped | 
**per_share_info** | [**[AgentConnectorPerShareStats]**](AgentConnectorPerShareStats.md) | Information collected from the shares. Each share currently exposed will have a single record in this list. Shares which were once exposed, but no longer are, do not have records. If a share is later exposed, its statistics will be reset.  | 
**server_start_time** | **datetime** | When the server was started. If the server has never started, this value will be ommitted.  | [optional] 
**server_stop_time** | **datetime** | When the server was stopped. If the server has never stopped, this value will be ommitted.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


