# RuleQueryBodyJSON

A unique name that refers to a specific constraint.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name that refers to a specific constraint. | 
**exact_match** | **str** | The value that&#39;s matched against and should be exactly the same to satisfy the rule. | [optional] 
**match_type** | **str** | The type of the value that&#39;s matched against. | [optional]  if omitted the server will use the default value of "string"
**pointer** | **str** | The json pointer path that system follows to store or retrieve data. The pointers are defined in (https://tools.ietf.org/html/rfc6901).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


