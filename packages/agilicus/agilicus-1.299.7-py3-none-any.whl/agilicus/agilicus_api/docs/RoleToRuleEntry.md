# RoleToRuleEntry

Associates a rule with a role. The association may either be to include the rule in the role's effective list of rules, or it may be to exclude it. If the rule is excluded, then if an included role itself includes this rule, the rule will not be included in the final list of rules for this role. A rule can be included in a role only once. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**RoleToRuleEntrySpec**](RoleToRuleEntrySpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


