# UserAttribute

A UserAttribute is a generic named attribute associated with a user. It can take on any value. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the attribute. All attributes with the same name will be merged when reading the actual user record for this attribute such that only a single value for a given name will result.  | 
**value** | **bool, date, datetime, dict, float, int, list, str, none_type** | The value of the attribute. This is a generic field to allow for use of any data from an identity provider.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


