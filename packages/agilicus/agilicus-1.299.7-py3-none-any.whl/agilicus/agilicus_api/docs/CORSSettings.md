# CORSSettings

CORSSettings controls the Cross-Origin Resource Sharing (CORS) policy of an Application. This allows an application to control which origins may request content from it. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether or not to apply the CORS policy. If the policy is disabled, then any CORS headers applied by the application will be passed through unchanged.  | 
**origin_matching** | **str** | How to match the origin. Note that in all cases the &#39;allow_origins&#39; list will be consulted.  - &#x60;me&#x60;: match the hosts on which this application can be reached.  - &#x60;wildcard&#x60;: match any host.  - &#x60;list&#x60;: match only those hosts provided in the &#x60;allow_origins&#x60; list.  | 
**allow_origins** | [**[CORSOrigin]**](CORSOrigin.md) | Lists the origins allowed to access the resources of this application. Any matching origin will have its value echoed back in the &#x60;Access-Control-Allow-Origin&#x60; header.  | 
**allow_methods** | **[str]** | The methods for which to allow access to resources. These correspond to the &#x60;Access-Control-Allow-Methods&#x60; header, into which they are joined by commas. If this value is null, then the methods are wildcarded. Set a value to &#39;*&#39; to wildcard.  | 
**allow_headers** | **[str]** | The headers which may be sent in a request to resources from this application. These correspond to the &#x60;Access-Control-Allow-Headers&#x60; header, into which they are joined by commas. If this value is null, then the headers are wildcarded. Set a value to &#39;*&#39; to wildcard.  | 
**expose_headers** | **[str]** | The response headers which the javascript running in the browser may access for resources from this application. These correspond to the &#x60;Access-Control-Expose-Headers&#x60; header, into which they are joined by commas. If this value is null, then the headers are wildcarded. Set a value to &#39;*&#39; to wildcard.  | 
**max_age_seconds** | **int** | This sets the &#x60;Access-Control-Max-Age&#x60; which controls the maximum number of seconds for which the results of the CORS preflight check may be cached. -1 disables caching.  | 
**allow_credentials** | **bool** | Whether credentials may be sent in requests. This corresponds to the &#x60;Access-Control-Allow-Credentials&#x60; header.  | 
**mode** | **str** | How the CORS settings are applied. - &#x60;overwrite&#x60;: CORS settings as configured overwrite any policy returned by the server.   This is the default behaviour. - &#x60;clear&#x60;: No CORS settings are applied. Any policy returned by the server is cleared out.  | [optional] 
**allow_resource_origins** | **bool** | When true, an Applications that have multiple ApplicationServices assigned to them will be allowed access according to the hostname configured for that service. See expose_as_hostnames in ApplicationService. When true, this setting will work in addition to the origin_matching configuration.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


