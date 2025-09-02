# ConnectorSecureTransferStatus

Status information pertaining to a ConnectorSecureTransfer. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expiry_time** | **datetime** | The expiry time for this transfer.  | [optional] 
**encrypted_data_length** | **int** | The length of encrypted data that has been stored.  | [optional] 
**status** | **str** | The status of the copy.  Can be defined as one of the following:   pending: secure transfer is pending. Not all information has been populated     for the transfer to proceed.   ready: secure transfer is ready. All information has been populated     and is ready for transfer to proceed.   expired: secure transfer is no longer valid and is expired  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


