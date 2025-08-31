# Icon

Describes an icon which can be used by software to represent something. Icons are accessible via a URI (e.g. https:// or file://). Various attributes describe the properties' of the icon which can help to decide whether or not is appropriate for a given client. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uri** | **str** | The URI at which to access this resource. | 
**purposes** | [**[IconPurpose]**](IconPurpose.md) | A list of reasons to use this icon. This could be a list of clients which use it, for example.  | 
**dimensions** | [**IconDimensions**](IconDimensions.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


