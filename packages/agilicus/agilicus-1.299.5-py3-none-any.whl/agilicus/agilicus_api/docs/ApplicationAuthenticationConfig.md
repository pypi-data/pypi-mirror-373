# ApplicationAuthenticationConfig

The configuration for application authentication options. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_handles_authentication** | **bool** | Whether the application should be forwarded requests when a user is unauthenticated so that the application can trigger authentication. If true, unauthenticated user requests will be forwarded to the application with a header indicating the user is unauthenticated. If false unauthenticated users will be denied and no traffic will reach the application.  | [optional] 
**session_secret** | **str** | A string which may be used to cipher session data -- e.g. a session cookie. This value will be passed to a running application in the &#x60;SESSION_SECRET&#x60; environment variable. If that variable is present in the instance&#39;s configured environment, the environment&#39;s configuration will take precedence. This value is automatically generated when an instance is created if not provided. It may be changed later. If the value is &#x60;\&quot;\&quot;&#x60; then the environment variable will not be provisioned. The automatically generated value is a base64-encoded series of random bytes. Aside from the base64 encoding, the value has no meaning.  | [optional] 
**upstream** | [**OIDCProxyUpstreamAuthentication**](OIDCProxyUpstreamAuthentication.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


