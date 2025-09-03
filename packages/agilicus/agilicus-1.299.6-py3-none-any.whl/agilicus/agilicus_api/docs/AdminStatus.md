# AdminStatus

The desired state for an entity. The active state indicates the entity is ready to operate. The disabled state indicates the entity has been disabled. The testing state indicates the entity is in a test mode. The deleted state indicates that this entity has been deleted. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The desired state for an entity. The active state indicates the entity is ready to operate. The disabled state indicates the entity has been disabled. The testing state indicates the entity is in a test mode. The deleted state indicates that this entity has been deleted.  |  must be one of ["active", "disabled", "testing", "deleted", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


