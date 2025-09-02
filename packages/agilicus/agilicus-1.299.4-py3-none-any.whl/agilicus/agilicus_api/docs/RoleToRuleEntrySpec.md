# RoleToRuleEntrySpec

The main definition of a `RoleToRuleEntry`. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_id** | **str** | Unique identifier | [optional] 
**rule_id** | **str** | Unique identifier | [optional] 
**app_id** | **str** | Unique identifier | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**included** | **bool** | Whether to include or exclude the rule in the role. If true, the rule is included. If false, it is excluded.  | [optional]  if omitted the server will use the default value of True
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


