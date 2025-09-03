# FrameOptionsSettings

Controls whether an object is allowed to render a page inside another container such as a `<frame>`. Corresponds to the X-Frame-Options header. This can be used to prevent a site from being embedded in another, or to prevent click jacking. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the FrameOptionsSettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the X-Frame-Options header. - &#x60;deny&#x60;: Denies ever loading the site from within a frame - &#x60;sameorigin&#x60;: Can only load the site within a frame on the same origin as the page   itself. - &#x60;clear&#x60;: Removes the X-Frame-Options header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the X-Frame-Options header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


