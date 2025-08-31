# CertSigningReqStatus

The status for a CertSigningReq

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**certificates** | [**[X509Certificate]**](X509Certificate.md) | The issued x509 certificates, formatted as PEM. This list is sorted by X509Certificate.not_before.  | [optional] 
**common_name** | **str** | The certificate common name (CN)  | [optional] [readonly] 
**dns_names** | [**[Domain]**](Domain.md) | The list of domains of which the CSR is requesting to be issued to. | [optional] [readonly] 
**connector_id** | **str** | Unique identifier | [optional] 
**auto_renew** | **bool** | The overall auto_renew status, which is a combination of the configured auto_renew status based on the CertSigningReqSpec, and the overall status of the agent connector (if applicable).  | [optional] 
**certificate_updates** | [**[X509Certificate]**](X509Certificate.md) | Certificate messages from cert manager related to progress or any failures that may have occured. These updates will be automatically removed by system as they will age out. This property is updated for queries that have set &#39;get_certificate_updates&#39; boolean to true.  This list is ordered with the first entry being the most recent update.  Any entries in this list will expire in 7 days.  The most recent 100 entries (maximum) will be returned (if available). Query parameters certificate_updates_start_cursor and certificate_updates_end_cursor can specify the range of updates to return in the query.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


