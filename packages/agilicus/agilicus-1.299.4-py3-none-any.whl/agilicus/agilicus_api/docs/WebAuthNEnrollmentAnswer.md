# WebAuthNEnrollmentAnswer

The contents of the WebAuthN enrollment answer.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | Unique identifier | [readonly] 
**credential_id** | **str** | A base64 encoding of the credential ID choosen by the authenticator | 
**client_data** | **str** | JSON encoded collection of key-value mappings representing the contextual bindings of the relying party and client | 
**authenticator_data** | **str** | Opaque string representing the authentication data, and attestion statements. | [optional] 
**signature** | **str** | The raw signature from the authenticator. This value is only included in the Authentication Assertion Response. For details see https://developer.mozilla.org/en-US/docs/Web/API/AuthenticatorAssertionResponse | [optional] 
**user_handle** | **str** | The user handle returned from the authenticator. This is optionally included in the Authentication Assertion Response. | [optional] 
**transports** | **[str]** | List of supported transports for this enrolled credential | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


