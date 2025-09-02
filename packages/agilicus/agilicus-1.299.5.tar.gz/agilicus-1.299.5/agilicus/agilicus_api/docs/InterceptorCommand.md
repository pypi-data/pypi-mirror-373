# InterceptorCommand

The configuration associated the interception of a process. If both name_exact and value_regex are specified, both will be utilized in the match (boolean OR). Eg.     command == name_exact OR command.regex(value_regex) 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name_exact** | **str** | The exact name of the command to match | [optional] 
**value_regex** | **str** | A regex describing the value to match the command. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


