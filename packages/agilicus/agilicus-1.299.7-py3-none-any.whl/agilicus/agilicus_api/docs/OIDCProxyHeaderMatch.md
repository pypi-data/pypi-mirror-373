# OIDCProxyHeaderMatch

Describes how to match a header. Any provided properties must match. E.g. if a name and value are provided, both the name and the value must match, whereas if only the name is provided, any headers of that name, regardless of the value, will match. If no properties are provided, nothing will match. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name_exact** | **str** | The header name that will be removed. The match is case insensitive. | [optional] 
**value_regex** | **str** | A regex describing the value to match. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


