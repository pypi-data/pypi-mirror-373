# AuditDestinationAuthentication

How an audit destination authenticates. For example, a webhook destination may require basic authentication. Not all destination types support all authentication schemes, nor do all audit agents. If the scheme is unsupported, the configuration may fail, leading to an error report. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**authentication_type** | **str** | The type of authentication to perform. The types have the following meanings:   - &#x60;none&#x60;: The destination is unauthenticated.   - &#x60;http_basic&#x60;: Uses HTTP basic (RFC7235) authentication. The username and password are provided in     the &#x60;http_basic&#x60; property.   - &#x60;http_bearer&#x60;: Uses HTTP bearer token (rfc6750) authentication. The token is provided     the &#x60;http_bearer&#x60; property.   - &#x60;agilicus_bearer&#x60;: Uses HTTP bearer token (rfc6750) authentication, with an access token from the     Agilicus infrastructure. The access token identifies the bearer as the &#x60;User&#x60; running the audit agent.   - &#x60;client_certificate&#x60;: Currently unsupported.  | 
**http_basic** | [**HTTPBasicAuth**](HTTPBasicAuth.md) |  | [optional] 
**http_bearer** | [**HTTPBearerAuth**](HTTPBearerAuth.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


