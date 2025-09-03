# IpsecConnector

An  IpsecConnector represents a routing next hop for a collection of services. Typically a single IpsecConnector connects the Agilicus cloud to multiple services running in a single data centre. An IpsecConnector comprises one or more tunnels (IpSecConnections), which combined form a logical tunnel providing redundancy and load-balancing. Distinct data centres providing distinct sets of services should each have their own IpsecConnector. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**spec** | [**IpsecConnectorSpec**](IpsecConnectorSpec.md) |  | [optional] 
**status** | [**IpsecConnectorStatus**](IpsecConnectorStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


