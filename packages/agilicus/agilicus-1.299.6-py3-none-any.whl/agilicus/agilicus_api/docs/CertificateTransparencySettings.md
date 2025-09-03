# CertificateTransparencySettings

Controls the Expect-CT header for certificate transparency.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether to apply the Certificate Transparency Settings. If false, no settings will be applied. Settings applied by the application itself will take effect.  | 
**enforce** | **bool** | Whether or not certificate transparency failures cause the browser to take action.  | 
**max_age_seconds** | **int** | The number of seconds for which to remember that the Application expects certificate transparency.  | 
**report_uri** | **str, none_type** | The uri where the browser will report failures. Setting this to &#x60;null&#x60; or &#x60;\&quot;\&quot;&#x60; will prevent reports.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


