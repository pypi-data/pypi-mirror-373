# FileShareService

A web-based file share exposed via the Agilicus Cloud. The share will be exposed via a files host with path `/{spec.share_name}`. A file share will create an associated ApplicationService which links it to the chosen Connector.  Multiple connectors may be used to expose file shares. This can be useful if two file shares are on different systems when using a connector with a local component such as an AgentConnector. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**FileShareServiceSpec**](FileShareServiceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**FileShareServiceStatus**](FileShareServiceStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


