# SimpleResourcePolicyTemplateStructureNode

Defines an entry in a simplified tree of rules to be evaluated in a policy pipeline. The underlying policy model is somewhat more complicated than this -- allowing a fair bit more flexibility. The SimpleResourcePolicyTemplate hides much of that complexity with a simple recursive structure.  `rule_name` points to a rule in the containing SimpleResourcePolicyTemplate. If it matches, then its actions are applied, and the children are recursively evaluated in priority order (from high to low). The actions of the first matching child evaluating are applied. The other children are ignored. If the result of the actions is `none` then the entire tree from here down is considered unmatched. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**priority** | **int** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | 
**rule_name** | [**StandaloneRuleName**](StandaloneRuleName.md) |  | 
**children** | [**[SimpleResourcePolicyTemplateStructureNode]**](SimpleResourcePolicyTemplateStructureNode.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


