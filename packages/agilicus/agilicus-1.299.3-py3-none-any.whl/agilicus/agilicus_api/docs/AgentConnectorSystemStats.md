# AgentConnectorSystemStats

Information about the AgentConnector itself, as well as the system on which it runs. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**os_version** | **str** | The version of the operating system on which the AgentConnector is running. | 
**os_uptime** | **int** | The length of time, in seconds, the operating system has been running. | 
**agent_uptime** | **int** | The length of time, in seconds, the AgentConnector has been running. If the AgentConnector restarts, this value will reset to zero.  | 
**agent_version** | **str** | The version of software currently running for this AgentConnector. This includes both the version number and the commit reference from which it was built.  | 
**agent_connector_id** | **str** | The identifier of the AgentConnector publishing these statistics. The AgentConnector publishes this information in order to ensure that an AgentConnector does not accidentally publish to the wrong endpoint.  | 
**agent_connector_org_id** | **str** | The organisation identifier of the AgentConnector publishing these statistics. The AgentConnector publishes this information in order to ensure that an AgentConnector does not accidentally publish to the wrong endpoint.  | 
**agent_release_train** | **str** | The release train followed by the AgentConnector. It uses this when checking for updates to determine which version of the AgentConnector should be installed.  | [optional] 
**hostname** | **str** | The hostname of the computer on which the AgentConnector is running. | [optional] 
**config_update_time** | **datetime** | The date-time when the connector last updated its running configuration from the API.  | [optional] 
**connector_instance_id** | **str** | The connector_instance_id (if applicable).  | [optional] 
**correct_file_permissions** | **bool** | True if connector has correct permissions to its working directory and config files, false otherwise.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


