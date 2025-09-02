# SimpleResourcePolicyTemplate

Contains a set of policy rules along with a simple relationship structure that allows users to define a simplified, tabular view of their policy for a given resource. The list of rules define the rules that may be used by the resource. The policy_structure defines how they are actually used: the order (priority) in which they are evaluated, as well as how they are nested, if at all.  `policy_structure` is essentially a list of trees. Each tree forms one compound rule which will be evaluated, in priority order (highest to lowest). The first matching tree's actions are taken. A given policy_structure can have a maximum depth of 6, including the root, and a maximum of 32 nodes.  Set the object_type and object id according to the resource to which this template applies 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**policy_structure** | [**[SimpleResourcePolicyTemplateStructure]**](SimpleResourcePolicyTemplateStructure.md) | The list of trees defining the structure of this policy.  | 
**rules** | [**[RuleConfig]**](RuleConfig.md) | The rules which may be used in the &#x60;policy_structure&#x60;. A given rule is only applied by the policy if it is referenced by at least one policy_structure node.  | 
**template_type** | **str** | The descriminator for the PolicyTemplate. Set this to &#x60;simple_resource&#x60; | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


