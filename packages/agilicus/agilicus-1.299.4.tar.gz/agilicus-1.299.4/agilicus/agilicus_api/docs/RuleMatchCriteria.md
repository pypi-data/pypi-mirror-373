# RuleMatchCriteria

How to match an extracted value. This compares the value extracted by `extract_name` in the enclosing matcher against one of the provided match values in this object. The left hand side of binary operations comes from the enclosing matcher. The right hand side comes from `this`. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operator** | **str** | The operator used to evaluate this condition. &#x60;undefined&#x60; means that the value could not be extracted or was of the wrong type.  - &#x60;equals&#x60;: checks that enclosing.value &#x3D;&#x3D; this.value. - &#x60;not_equals&#x60;: checks that enclosing.value !&#x3D; this.value. - &#x60;greater_than&#x60;: checks that enclosing.value &gt; this.value. - &#x60;less_than&#x60;: checks that enclosing.value &lt; this.value. - &#x60;in&#x60;: checks that enclosing.value is in this.value, assuming this.value is a list. - &#x60;not_in&#x60;: checks that enclosing.value is not in this.value, assuming this.value is a list. - &#x60;undefined&#x60;: checks that enclosing.value is undefined.  | [optional] 
**match_literal** | **bool, date, datetime, dict, float, int, list, str, none_type** | A literal value to match against | [optional] 
**match_extractor** | **str** | The name of an extractor to match against. This allows for asserting that two values of a request are the same.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


