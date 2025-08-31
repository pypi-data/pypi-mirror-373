# XSSSettings

Controls the X-XSS-Protection header. Note: this may not be supported in all modern browsers, which have transitioned to Content Security Policy (CSP) as the mechanism to define cross site scripting behaviour. However, older browsers may not implement CSP to the required level, and may implement X-XSS-Protection. In that case, configuring this header will have no negative impact on modern browsers (which will ignore it), but can provide compatibility with older ones. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether or not to send the XSS-Protection-Header. If false, the system will not add the XSS-Protection-Header. Any headers added by the application will be passed through unchanged.  | 
**mode** | **str** | Mode controls whether or not XSS filtering is enabled, and how it is. It has the following meanings:   - &#x60;disabled&#x60;: XSS Filtering is disabled.   - &#x60;sanitise&#x60;: XSS Filtering is enabled. Pages being attacked are sanitised.   - &#x60;block&#x60;: XSS Filtering is enabled, and attacked pages are not rendered.  | 
**report_uri** | **str, none_type** | Detected attacks are reported to this URI for supported browsers. Omitting this field or setting it to \&quot;\&quot; will lead to not reports being generated  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


