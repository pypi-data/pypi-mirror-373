# RenderedRuleBody

Body describes constraints on the request. It helps to prevent users from modifying special fields(e.g. userid) in the body to gain extra access rights in the system. The format of the body(e.g. JSON) is specified below with the restriction. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**json** | [**[JSONBodyConstraint]**](JSONBodyConstraint.md) | Array of json body constraints | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


