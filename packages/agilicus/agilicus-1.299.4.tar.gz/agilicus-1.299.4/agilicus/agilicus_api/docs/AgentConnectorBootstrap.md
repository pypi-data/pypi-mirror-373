# AgentConnectorBootstrap

Information used to bootstrap an AgentConnector. This includes an API Key with permission to create the connector authentication document, and an optional challenge to respond to when the connector comes online for the first time. This challenge is useful to quickly hint back to the caller that the installation was succesful. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_key** | **str** | The secret api key that can be used to bootstrap the connector  | 
**api_key_user** | **str** | The username/email/etc to provide alongside the api key when authenticating using it.  | 
**issuer** | **str** | The url of the issuer for the connector to log in to  | 
**connector_id** | **str** | The unique ID of the connector  | 
**org_id** | **str** | The unique ID of the organisation the connector belongs to.  | 
**join_cluster** | **bool** | Whether to join a cluster or create a new one. If false or not set, a new cluster is created | [optional] 
**response_challenge_id** | **str** | The ID of a challenge to respond to indicating that the install finished.  | [optional] 
**response_challenge_code** | **str** | The code of a challenge to respond to indicating that the install finished.  | [optional] 
**session_context** | **str** | A session-context string for analytics cross-join purposes.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


