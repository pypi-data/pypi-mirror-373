# SourceInfoPolicyTemplate

Restricts access to resources based on the source from which a request originates. If invert is true, the policy will match requests whose ip does not match one of the items in source_subnets and iso_country_codes. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**labels** | [**[LabelName]**](LabelName.md) | Restrict the challenge to accesses for resources with one of these labels.  | 
**template_type** | **str** | The descriminator for the PolicyTemplate. Set this to &#x60;source_info&#x60; | 
**source_subnets** | **[str]** | A list of IP subnets. If the request comes from one of them, it will be allowed or denied based on the provided configuration.  | 
**iso_country_codes** | **[str]** | A list of ISO 3166-1 alpha-2 country codes. If the request comes from one of them, it will be allowed or denied based on the provided configuration.  | 
**invert** | **bool** | If set to true, will match the request if the source ip is not in the source_subnets list, and the country code is not in the iso_country_codes list.  | 
**action** | **str** | If set to allow, the request will be allowed if it matches. If set to deny, it will be denied.  | 
**log_message** | **str** | If set, will emit a log message with this avalue on match | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


