# StandaloneRulePolicy

Defines the policy for a subset of the system by providing an aggregation point for the rules primitives which make up that policy. The main purpose of the StandaloneRulePolicy is to define ownership by linking a policy to an external component of the system (e.g. a PolicyTemplate or Resource), which allows for easily querying related rules primitives and performing lifecycle tasks like garbage collection.  The link between the StandaloneRulePolicy and the external object is defined by the following five-tuple:   - object_type   - object_id   - policy_class   - policy_name   - org_id  Genernally the object_type and object_id are set together, as are policy_class and policy_name. For example, the existing default 'firewall rules' for an application called X could have:  - object_type: application  - object_id: application.id  - policy_class: null  - policy_name: null Whereas a policy template called Y for that same application would have:  - object_type: application  - object_id: application.id  - policy_class: prefix_redirect  - policy_name: Y And a global multifactor policy template called Z would have:  - object_type: null  - object_id: null  - policy_class: mfa  - policy_name: Z This facilitiates the following operations, for example:   - Find all RuleSets for a given resource   - Find all RulePolicies for a given policy template type (aka find all instances of that policy)   - Find all RuleTrees for a given PolicyTemplate instance   - Delete all primitives associated with a PolicyTemplate instance   - Delete all primitives associated with a resource 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**StandaloneRulePolicySpec**](StandaloneRulePolicySpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


