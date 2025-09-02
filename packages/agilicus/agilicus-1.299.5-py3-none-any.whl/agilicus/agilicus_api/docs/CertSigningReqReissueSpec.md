# CertSigningReqReissueSpec

A request to reissue a certificate. For CSRs which support manual recreation of a certificate, this will force them to kickstart a process whereby a new certificate is created. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**csr_id** | **str** | The CertSigningReq id to reissue. | 
**old_not_after** | **datetime** | The not_after_time of the last available certificate. Updating this value to a time later than the currently set value will generate a new certificate. By using the not after time of the previously generated certificate, multiple consumers of certificates can coordinate without racing to generate extraneous certificates.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


