# CrossOriginEmbedderPolicySettings

Controls the Cross Origin Embedder Policy (COEP) for the site. Corresponds to the Cross-Origin-Embedder-Policy header. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the CrossOriginEmbedderPolicySettings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**mode** | **str** | Controls the value of the Cross-Origin-Embedder-Policy header. - &#x60;unsafe_none&#x60;: Allows fetching of cross-origin resources without having explicit permission   to do so via CORS (Cross Origin Resource Sharing) or CORP (Cross Origin Resource Policy). This is the default. - &#x60;require_corp&#x60;: Can only fetch and load resources from the same origin, or which have been    marked as loadable from a different origin. Either a crossorigin attribute in conjunction    with CORS, or permission from the CORP must be given in order to    load the resource. - &#x60;clear&#x60;: Removes the Cross-Origin-Embedder-Policy header from the server&#39;s response if present. - &#x60;override&#x60;: Use the value specified in the override field. If it is not present, the   header will be set to an empty string.  | 
**override** | **str, none_type** | Set a specific value for the Cross-Origin-Embedder-Policy header. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


