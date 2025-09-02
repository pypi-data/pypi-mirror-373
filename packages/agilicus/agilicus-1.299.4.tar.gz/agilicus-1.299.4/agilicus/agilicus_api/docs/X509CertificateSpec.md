# X509CertificateSpec

A X509CertificateSpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**reason** | [**CSRReasonEnum**](CSRReasonEnum.md) |  | 
**ca** | **str** | The PEM certificate authority associated with this certificate. | [optional] 
**certificate** | **str** | The issued x509 certificate, formatted as PEM. | [optional] 
**encryption_key_id** | **str** | A unique identifier used to identify the encryption key that was used for encryption of the priv_key, output of encrypted_priv_key.  | [optional] 
**encrypted_priv_key** | **str** | The encrypted private key | [optional] 
**csr_id** | **str** | The CertSigningReq id associated with this certificate | [optional] 
**message** | **str** | A system message associated with the reason.  | [optional] 
**certificate_tracker_id** | **str** | The CertificateTracker id associated with this certificate, if applicable.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


