# PolicyTemplate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template_type** | **str** | The descriminator for the PolicyTemplate. Set this to &#x60;simple_resource&#x60; | 
**log_message** | **str** | If set, will emit a log message with this avalue on match | [optional] 
**seconds_since_last_challenge** | **int** | Challenge the user if they have not presented a second factor for the current session in the last N seconds.  | [optional] 
**labels** | [**[LabelName]**](LabelName.md) | Restrict the challenge to accesses for resources with one of these labels.  | [optional] 
**source_subnets** | **[str]** | A list of IP subnets. If the request comes from one of them, it will be allowed or denied based on the provided configuration.  | [optional] 
**iso_country_codes** | **[str]** | A list of ISO 3166-1 alpha-2 country codes. If the request comes from one of them, it will be allowed or denied based on the provided configuration.  | [optional] 
**invert** | **bool** | If set to true, will match the request if the source ip is not in the source_subnets list, and the country code is not in the iso_country_codes list.  | [optional] 
**action** | **str** | If set to allow, the request will be allowed if it matches. If set to deny, it will be denied.  | [optional] 
**original_template_type** | **str** | The original type of the template. | [optional] 
**policy_structure** | [**[SimpleResourcePolicyTemplateStructure]**](SimpleResourcePolicyTemplateStructure.md) | The list of trees defining the structure of this policy.  | [optional] 
**rules** | [**[RuleConfig]**](RuleConfig.md) | The rules which may be used in the &#x60;policy_structure&#x60;. A given rule is only applied by the policy if it is referenced by at least one policy_structure node.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


