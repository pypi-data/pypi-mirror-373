# RuleQueryParameter

Each instance maps a particular query parameter to a set of constraints.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the query parameter. | 
**exact_match** | **str** | The given query parameter must exist and equal this. Can be templatized with jinja2 using the definitions collection.  This property has been updated to support regex style matching. For regex, set the match_type to &#39;regex&#39;.  | [optional] 
**match_type** | **str** | The default match_type (when ommitted) is &#39;exact&#39;, for backwards compatibility. Other match types supported is &#39;regex&#39;.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


