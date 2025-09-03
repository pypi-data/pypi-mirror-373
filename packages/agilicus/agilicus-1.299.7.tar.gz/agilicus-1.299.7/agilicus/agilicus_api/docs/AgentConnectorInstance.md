# AgentConnectorInstance

An installed instance of an AgentConnector. A specific AgentConnector guid can be installed on multiple devices for high availability. For each running/installed instance, each device uniquely creates an AgentConnectorInstance. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**AgentConnectorInstanceSpec**](AgentConnectorInstanceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**AgentConnectorInstanceStatus**](AgentConnectorInstanceStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


