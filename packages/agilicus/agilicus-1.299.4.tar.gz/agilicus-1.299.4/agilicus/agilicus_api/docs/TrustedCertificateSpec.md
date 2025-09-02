# TrustedCertificateSpec


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificate** | **str** | The issued x509 certificate, formatted as PEM. | 
**root** | **bool** | When true, this certificate is trusted as a root certificate.  | [optional]  if omitted the server will use the default value of False
**org_id** | **str** | Unique identifier | [optional] 
**labels** | [**[TrustedCertificateLabelName]**](TrustedCertificateLabelName.md) | list of labels associated with certificate | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


