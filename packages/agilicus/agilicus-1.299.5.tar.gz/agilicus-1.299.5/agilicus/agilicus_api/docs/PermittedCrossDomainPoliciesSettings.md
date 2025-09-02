# PermittedCrossDomainPoliciesSettings

Controls a cross domain policy used to indicate to clients of resources such as Flash or PDF whether they can load content from your site. Corresponds to the X-Permitted-Cross-Domain-Policies header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the PermittedCrossDomainPoliciesSettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the X-Permitted-Cross-Domain-Policies header. - &#x60;clear&#x60;: Removes the X-Permitted-Cross-Domain-Policies header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the X-Permitted-Cross-Domain-Policies header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


