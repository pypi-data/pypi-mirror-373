# APIKey

A key which may be used to access the system without the need for an explicit login. This essentially serves as a layer of indirection to a normal access token. It can be used for cases where an access token is not user friendly (e.g. systems that only support basic auth). An API Key is scoped in the same fashion as an access token: it has constraints such as an organisation; it is associated to a user; it can be revoked; it can expire, and so on. In order to use an API Key, present it using http basic authentication using your email address as the user name. Note that API Keys are not as secure as short lived access tokens or service account authentication documents, so only use them where necessary. It is best to place an expiry on them so that if they do leak, they are limited in the damage they can do.  The actual key to use in your requests will be present in the status, but only on creation. If you lose the API Key, delete this one and create a new one.  Note that to have this API key represent suborganisations, you must request the 'urn:agilicus:token_payload:multiorg:true' scope. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**APIKeySpec**](APIKeySpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**APIKeyStatus**](APIKeyStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


