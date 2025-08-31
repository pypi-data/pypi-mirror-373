# NetworkMountRuleConfig

A NetworkMountRuleConfig configures how a set of clients mount a share. This enables configuration like 'windows shop computers mount share x to the y: drive'. If there are no rules, then all users with access to this share will mount automatically. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rules** | [**ResourceRuleGroup**](ResourceRuleGroup.md) |  | 
**mount** | [**FileShareClientConfig**](FileShareClientConfig.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


