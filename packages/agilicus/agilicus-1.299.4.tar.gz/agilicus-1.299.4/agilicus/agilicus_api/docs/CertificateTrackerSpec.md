# CertificateTrackerSpec

The spec for a CertificateTracker 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The organisation to which the CertificateTracker is associated with.  | 
**config** | [**CertificateTrackerConfig**](CertificateTrackerConfig.md) |  | 
**uid** | **str** | An optional, unique identifying id (UID), that could associate this CertificateTracker to an external Certificate (for example, kubernetes UID)  | [optional] 
**max_certificate_history** | **int** | Sets the maximum number of certificates that will be maintained, before auto-deleting them.  | [optional]  if omitted the server will use the default value of 3
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


