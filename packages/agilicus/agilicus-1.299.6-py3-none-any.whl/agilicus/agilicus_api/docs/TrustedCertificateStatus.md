# TrustedCertificateStatus


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**not_before** | **datetime** | date/time for which certificate is valid | [optional] [readonly] 
**not_after** | **datetime** | date/time of certificate expiry | [optional] [readonly] 
**serial_number** | **str** | the certificate serial number | [optional] [readonly] 
**issuer** | **str** | the certificate issuer | [optional] [readonly] 
**subject** | **str** | certificate subject | [optional] [readonly] 
**subject_sha1** | **str** | certificate subject sha128 hash | [optional] [readonly] 
**subject_sha256** | **str** | certificate subject sha256 hash | [optional] [readonly] 
**public_key_sha1** | **str** | public key DER sha128 hash | [optional] [readonly] 
**public_key_sha256** | **str** | public key DER sha256 hash | [optional] [readonly] 
**skid** | **str** | The Subject Key Identifier | [optional] [readonly] 
**akid** | **str** | The Authority Key Identifier | [optional] [readonly] 
**ca** | **bool** | true if the certificate is a certificate authority, otherwise false | [optional] [readonly] 
**key_usage_extension** | **str** | the certificate key usage extension | [optional] [readonly] 
**digital_signature** | **bool** | This purpose is set to true when the subject public key is used for verifying digital signatures, other than signatures on certificates (key_cert_sign) and CRLs (crl_sign).  | [optional] [readonly] 
**content_commitment** | **bool** | This purpose is set to true when the subject public key is used for verifying digital signatures, other than signatures on certificates (key_cert_sign) and CRLs (crl_sign). It is used to provide a non-repudiation service that protects against the signing entity falsely denying some action. In the case of later conflict, a reliable third party may determine the authenticity of the signed data. This was called non_repudiation in older revisions of the X.509 specification.  | [optional] [readonly] 
**key_encipherment** | **bool** | This purpose is set to true when the subject public key is used for enciphering private or secret keys.  | [optional] [readonly] 
**data_encipherment** | **bool** | This purpose is set to true when the subject public key is used for directly enciphering raw user data without the use of an intermediate symmetric cipher.  | [optional] [readonly] 
**key_agreement** | **bool** | This purpose is set to true when the subject public key is used for key agreement. For example, when a Diffie-Hellman key is to be used for key management, then this purpose is set to true.  | [optional] [readonly] 
**key_cert_sign** | **bool** | This purpose is set to true when the subject public key is used for verifying signatures on public key certificates. If this purpose is set to true then ca must be true in the BasicConstraints extension.  | [optional] [readonly] 
**crl_sign** | **bool** | This purpose is set to true when the subject public key is used for verifying signatures on certificate revocation lists.  | [optional] [readonly] 
**encipher_only** | **bool** | When this purposes is set to true and the key_agreement purpose is also set, the subject public key may be used only for enciphering data while performing key agreement.  | [optional] [readonly] 
**decipher_only** | **bool** | When this purposes is set to true and the key_agreement purpose is also set, the subject public key may be used only for deciphering data while performing key agreement.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


