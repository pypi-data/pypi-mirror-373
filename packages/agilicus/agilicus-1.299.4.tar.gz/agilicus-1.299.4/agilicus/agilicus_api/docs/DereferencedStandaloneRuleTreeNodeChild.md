# DereferencedStandaloneRuleTreeNodeChild

Defines a child tree of a DereferenedStandaloneRuleTreeNode. The priority, unique amongst siblings, defines the order in which the siblings are evaluated (highest to lowest). The node is the child tree. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**priority** | **int** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | 
**node** | [**DereferencedStandaloneRuleTreeNode**](DereferencedStandaloneRuleTreeNode.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


