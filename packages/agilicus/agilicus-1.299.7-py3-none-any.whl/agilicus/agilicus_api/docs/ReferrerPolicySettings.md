# ReferrerPolicySettings

Controls how much information is sent via the Referer header. Corresponds to the Referrer-Policy header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the ReferrerPolicySettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the Referrer-Policy header. - &#x60;no_referrer&#x60;: The Referer header will not be sent by the client. - &#x60;no_referrer_when_downgrade&#x60;: Only send the Referer header when the protocol&#39;s security does not degrade.   (e.g. HTTPS to HTTP will lead to the header header not being sent). - &#x60;origin&#x60;: Only send the origin in the Referer header. - &#x60;origin_when_cross_origin&#x60;: Only send the origin in the Referer header when making cross origin requests.    Same-origin requests send the entire referer. - &#x60;same_origin&#x60;: Only send the origin in the Referer header for same-origin requests. - &#x60;strict_origin&#x60;: Send only the origin, and only then when the protocol&#39;s security is    HTTPS. - &#x60;strict_origin_when_cross_origin&#x60;: Send the full Referer header for same-origin requests.    Send only the origin for cross-origin requests. Do not send any Referer header when the protocol&#39;s    security degrades. This option is the default behaviour for most clients. - &#x60;unsafe_url&#x60;: Always send the entire Referer header. Warning: this setting could potentially leak private    or sensitive information contained in URLs. - &#x60;clear&#x60;: Removes the Referrer-Policy header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the Referrer-Policy header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


