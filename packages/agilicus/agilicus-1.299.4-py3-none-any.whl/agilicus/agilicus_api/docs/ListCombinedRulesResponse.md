# ListCombinedRulesResponse

The response object for listing combined rules. This will containe the list of rules corresponding to the query, combined based on related fields. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **int** | The maximum number of CombinedRules that could be returned in the response.  | 
**combined_rules** | [**[CombinedRules]**](CombinedRules.md) | The combined rules matching the search criteria | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


