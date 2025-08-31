# StandaloneRulePolicySpec

The specification of a StandaloneRulePolicy. A StandaloneRulePolicy is uniquely identified by: (org_id, object_type, object_id, policy_class, policy_instance). When a given key in the primary key does not matter, put \"\". 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**object_type** | [**EmptiableObjectType**](EmptiableObjectType.md) |  | 
**object_id** | **str** | Unique identifier | 
**policy_class** | **str** | Used to distinguish between different &#39;classes&#39; of policy which each provide a certain type of functionality. For example, a templating system might give each template a unique class, distinguishing different sets of paremeters for a given template with a different policy_instance. Null means that this policy doesn&#39;t fall into any particular category.  | 
**policy_instance** | **str** | Used to distinguish between different policies of a given class. For example, an org may have two policies with class &#x60;mfa&#x60;, but different parameters. Those two would have a different &#39;instance&#39;. The caller is responsible for ensuring a unique instance where necessary.  | 
**description** | [**StandaloneRulePolicyDescription**](StandaloneRulePolicyDescription.md) |  | [optional] 
**annotations** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | A simple object used to track details about how the policy is used (E.g. template version).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


