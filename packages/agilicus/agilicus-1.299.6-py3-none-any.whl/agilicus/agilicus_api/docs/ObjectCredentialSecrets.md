# ObjectCredentialSecrets

The portion of the object credentials which contains sensitive infomration. It is write once. The actual credentials are typically returned encrypted in the status. How and whether they are encrypted depends on the encrypt and encryption_key_id parameters. Note that neither of those may be changed once a credential has been created. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encrypt** | **bool** | Whether the data should be encrypted. If so, then the encryption_key_id must either be blank (in which case the system will choose one), or it must exist in the system, and the corresponding public key will be used to encrypt the data. If it is false, then the data will be stored as-is. If you also set the encryption_key_id, then the data will be considered encrypted by that key already.  | [optional]  if omitted the server will use the default value of True
**encryption_key_id** | **str** | The hex value of the sha256 hash of the public key&#39;s binary data.  | [optional] 
**username** | **str** | The username to present to the server. | [optional] 
**private_key** | **str** | The private key, in pem format, to present to the server.  | [optional] 
**private_key_passphrase** | **str** | Used to decrypt the private key if it has a passphrase.  | [optional] 
**password** | **str** | The password to present to the server. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


