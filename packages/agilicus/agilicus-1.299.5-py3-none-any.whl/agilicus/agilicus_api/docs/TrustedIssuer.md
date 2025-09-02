# TrustedIssuer

A trusted issuer maps to another OIDC issuer provided by Agilicus. This differs from normally configured issuers in that the only necessary configuration is the issuer URL and purpose. The system will take care of handling authentication of the clients, which simplifies the configuration. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issuer** | **str** | The issuer uri which identifies the whether to allow a user to log in, which identifies the OIDC endpoint at which  to authenticate  | [optional] 
**purpose** | **str** | The purpose of trusting this issuer, imposing additional restrictions on how users authenticate when accessing this upstream.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


