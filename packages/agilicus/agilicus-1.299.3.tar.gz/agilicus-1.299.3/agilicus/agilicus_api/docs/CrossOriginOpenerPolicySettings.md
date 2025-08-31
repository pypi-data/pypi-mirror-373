# CrossOriginOpenerPolicySettings

Controls the Cross Origin Opener Policy (COOP) for the site. Corresponds to the Cross-Origin-Opener-Policy header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the CrossOriginOpenerPolicySettings.  If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the Cross-Origin-Opener-Policy header. - &#x60;unsafe_none&#x60;: Allows the document to be be added to the popup&#39;s context, unless the opening   document has &#x60;same_origin&#x60; or &#x60;same_origin_allow_popups&#x60;. This is the default. - &#x60;same_origin_allow_popups&#x60;: Allows documents which don&#39;t have COOP, or set it to &#x60;unsafe_none&#x60;    to reference this document from their windows or tabs.    load the resource. - &#x60;same_origin&#x60;: Only documents from the same origin can reference this one. - &#x60;clear&#x60;: Removes the Cross-Origin-Opener-Policy  header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the Cross-Origin-Opener-Policy header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


