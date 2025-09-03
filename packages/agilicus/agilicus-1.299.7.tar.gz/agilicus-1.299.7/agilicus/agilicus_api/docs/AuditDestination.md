# AuditDestination

A destination for audit events. Each event may be sent to multiple destinations. The list of destinations for an organisation controls where event sources send events. Each destination can filter events so that it only captures relevant ones. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**AuditDestinationSpec**](AuditDestinationSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


