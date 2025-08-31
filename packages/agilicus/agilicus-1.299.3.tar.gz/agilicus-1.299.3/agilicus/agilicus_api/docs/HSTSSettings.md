# HSTSSettings

The configuration for HTTP Strict Transport Security (HSTS). These control settings which help to prevent man-in-the-middle attacks by requiring that all accesses to the Application's domains be made over HTTPS. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether or not to send the HSTS header. If disabled, any HSTS headers set by the application will be passed through unchanged.  | 
**max_age_seconds** | **int** | The number of seconds for which to remember that accesses need to be over HTTPS. A value of 0 means that the browser should forget.  | 
**include_sub_domains** | **bool** | Whether subdomains of the Application should be included in the HSTS restriction.  | 
**preload** | **bool** | Indicate to HSTS preload services that this application should be preloaded.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


