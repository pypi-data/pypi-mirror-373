# StandaloneRuleset

Builds a forest of rules which are all applied together. The rules engine applies each tree in priority (highest to lowest value) order, stopping evaluation once one tree has matched. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**StandaloneRulesetSpec**](StandaloneRulesetSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**StandaloneRulesetStatus**](StandaloneRulesetStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


