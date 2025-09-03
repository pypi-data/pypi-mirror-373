# AuthenticationDocumentSpec

The configuration for an authentication document. An authentication document is used to generate identity assertions that are used to authenticate a service account. Deleting an authentication document is equivilent to revoking the document's ability to request tokens. The key field is returned on creation only as this is a private key that must be keep secure. It is not stored by Agilicus. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The user id requesting an authentication document | 
**org_id** | **str** | The org id for the user requesting an authentication document | 
**auth_issuer_url** | **str** | The URL of the authentication issuer associated with this authentication document. This URL is used by service accounts to request a token. | [optional] 
**expiry** | **datetime** | The authentication document expiry time in UTC. If ommitted the document does not expire. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


