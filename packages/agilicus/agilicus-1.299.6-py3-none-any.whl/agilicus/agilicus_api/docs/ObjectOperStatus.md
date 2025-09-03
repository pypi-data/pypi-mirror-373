# ObjectOperStatus

The status of an object - active: the object is active and operating as specified - pending_delete: the object is waiting to be deleted. Its underlying data or resources may still exist. - deleted: the object has been deleted. Its underying data or resources have been removed. - down: the object is not operating as specified. For example, it may have lost connectivity. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The status of an object - active: the object is active and operating as specified - pending_delete: the object is waiting to be deleted. Its underlying data or resources may still exist. - deleted: the object has been deleted. Its underying data or resources have been removed. - down: the object is not operating as specified. For example, it may have lost connectivity.  |  must be one of ["active", "pending_delete", "deleted", "down", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


