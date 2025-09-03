# CredentialPurpose

The purpose of a credential. This allows a given object to store multiple credentials which may be accessed for different purposes, such as credential stuffing vs mutual TLS. Agilicus supports some default ones:   - `stuffing`:  This credential will be used for credential stuffing.     For example, you can configure an SSH Resource to present a private key without the end     user ever seeing it. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The purpose of a credential. This allows a given object to store multiple credentials which may be accessed for different purposes, such as credential stuffing vs mutual TLS. Agilicus supports some default ones:   - &#x60;stuffing&#x60;:  This credential will be used for credential stuffing.     For example, you can configure an SSH Resource to present a private key without the end     user ever seeing it.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


