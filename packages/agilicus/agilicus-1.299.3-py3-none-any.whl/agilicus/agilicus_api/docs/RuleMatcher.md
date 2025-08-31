# RuleMatcher

An object describing a match requirement for a rule. A rule matcher matches a value extracted from a request using the criteria defined here. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extractor_name** | **str** | Specifies the extractor to use to get value to match against. | 
**inverted** | **bool** | Whether the match is inverted. If the match is inverted, then it evaluates to false if and only if its match criteria evaluate to true. This can be useful to exclude something from a rule. E.g. \&quot;allow this path only if its first capture group does not equal 5\&quot;  | 
**join_operation** | **str** | How to join the criteria.  - &#x60;and&#x60;: All criteria must be true - &#x60;or&#x60;: One of the criteria must be true  | defaults to "and"
**criteria** | [**[RuleMatchCriteria]**](RuleMatchCriteria.md) | The list of the criteria to match, joined using &#x60;join_operation&#x60;. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


