# ObjectCredentialStatus

The read-only, inferred properties of the ObjectCredential. Includes the possibly encrypted secrets. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_encrypted** | **bool** | Whether or not the credentials returned here are encrypted.  | [optional] 
**encryption_key_id** | **str** | The hex value of the sha256 hash of the public key used to encrypt the data.  | [optional] 
**username** | **str** | The username to present to the server | [optional] 
**private_key** | **str** | The private key, in pem format, possibly encrypted, to present to the server.  | [optional] 
**private_key_passphrase** | **str** | Used to decrypt the private key if it has a passphrase. Possibly encrypted.  | [optional] 
**password** | **str** | The password to present to the server. Possibly encrypted. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


