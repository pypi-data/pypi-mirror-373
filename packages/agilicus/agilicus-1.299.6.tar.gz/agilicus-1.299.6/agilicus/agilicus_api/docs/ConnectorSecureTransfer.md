# ConnectorSecureTransfer

The connector secure transfer is a mechanism that allows for a secure transfer of data between connector instances within the same connector id. This is useful when connector instances need to share information, such as a private key for certificates.  The secure copy utilizes ECDH, Eliptic Curve Diffie Helman. Each instance creates their own, one time private/public keys. The public keys are shared between the instances, and then the transfer of the encrypted data can proceed (using DH, using its own private key in combination with the peer public key).  An ConnectorSecureTransfer instance can only be used once, and will timeout if the transfer does not proceed within an configurable period.  The initiation of the secure copy is access controlled by 'owner' of a connector. Only the owner can initiate this. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**ConnectorSecureTransferSpec**](ConnectorSecureTransferSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**ConnectorSecureTransferStatus**](ConnectorSecureTransferStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


