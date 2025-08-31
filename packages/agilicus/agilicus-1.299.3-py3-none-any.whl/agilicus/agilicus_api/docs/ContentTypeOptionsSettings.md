# ContentTypeOptionsSettings

Controls how the client should interpret the media type of the response (e.g. as determined from the Content-Type header). Corresponds to to the X-Content-Type-Options header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the ContentTypeOptionsSettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the X-Content-Type-Options header. - &#x60;nosniff&#x60;: Blocks the request if it doesn&#39;t align with the destination element. Also enables   Cross-Origin Read Blocking (CORB) protection for certain mime types. - &#x60;clear&#x60;: Removes the X-Content-Type-Options header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the X-Content-Type-Options header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


