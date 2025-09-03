# RuleMatcherList

Extensions to the rule allowing for more complicated matching logic such as numerical comparisons. Each matcher must be matched in order for the rule to evaluate to true according to the `join_operation`. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**matchers** | [**[RuleMatcher]**](RuleMatcher.md) | The matchers to evaluate using the &#x60;join_operation&#x60;. | 
**join_operation** | **str** | How to join the matchers.  - &#x60;and&#x60;: All matchers must be true - &#x60;or&#x60;: One of the matchers must be true  | defaults to "and"
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


