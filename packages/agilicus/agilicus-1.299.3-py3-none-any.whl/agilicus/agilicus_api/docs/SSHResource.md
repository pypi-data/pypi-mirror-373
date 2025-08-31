# SSHResource

A SSH Terminal exposed via the Agilicus Cloud. Access the machine using a client, supporting SSH protocol. You may expose multiple machines by creating multiple SSHResource objects. A Connector provides connectivity between the Agilicus Cloud and your machine so that you do not have to expose the machine to the Internet. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**SSHResourceSpec**](SSHResourceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**SSHResourceStatus**](SSHResourceStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


