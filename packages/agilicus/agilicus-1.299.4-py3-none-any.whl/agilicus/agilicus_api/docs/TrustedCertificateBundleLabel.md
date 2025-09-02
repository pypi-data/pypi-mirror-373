# TrustedCertificateBundleLabel

A label that is part of a bundle and its associated operation. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exclude** | **bool** | if true, the certs with the label are excluded from the bundle. When a label is excluded, it takes precendence over included rules, such that if a certificate were to labeled with both an exclude and not exclude label, the result would be that cert to be excluded.  | [optional] 
**label** | [**TrustedCertificateLabelSpec**](TrustedCertificateLabelSpec.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


