# CrossOriginResourcePolicySettings

Controls the Cross Origin Resource Policy (CORP) for the site. Corresponds to the Cross-Origin-Resource-Policy header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the CrossOriginResourcePolicySettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the Cross-Origin-Resource-Policy header. - &#x60;same_site&#x60;: Requests from the same site can read the resource. Note that this is different than &#x60;same_origin&#x60;.   For example, \&quot;https://example.com\&quot; is the same site as \&quot;https://my-app.example.com\&quot;. - &#x60;same_origin&#x60;: Only requests from the same origin can read the resource. - &#x60;cross_origin&#x60;: Requests from any origin can read the resource. - &#x60;clear&#x60;: Removes the Cross-Origin-Resource-Policy  header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the Cross-Origin-Resource-Policy header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


