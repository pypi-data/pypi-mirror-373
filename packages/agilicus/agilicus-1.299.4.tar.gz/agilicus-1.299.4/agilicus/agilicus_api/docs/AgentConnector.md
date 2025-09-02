# AgentConnector

A secure agent connector establishes a tunnel between the Agilicus infrastructure and the Secure Agent running on site. Its configuration controls how that link is established, how many connections are maintained and so on. Typically a connector corresponds to an Application running in the Agilicus infrastructure which provides the ingress side of the Secure Agent tunnel. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**AgentConnectorSpec**](AgentConnectorSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**AgentConnectorStatus**](AgentConnectorStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


