# RuleV2

A Rule defines a set of conditions which, if matched, allow a request to proceed through the system. If no rules match, the request will be denied. The Rule is a base class, with more concrete classes specifying precise match conditions. Rules may be associated with roles to allow for users to be granted collections of rules. Rules are uniquely identified by their id. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**RuleSpec**](RuleSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


