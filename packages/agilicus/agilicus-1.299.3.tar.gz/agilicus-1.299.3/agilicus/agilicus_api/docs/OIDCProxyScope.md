# OIDCProxyScope

An OIDCProxyScope describes a OIDC scope that will be used when authenticating with the configured OIDC provider. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Each application role represents a scope in the form of urn:agilicus:app:X:Y (X is the app name and Y is the role). The scope can be optional by adding a question mark after the role (e.g. urn:agilicus:app:X:Y?). If the scope is required, users without equivalent roles will be denied access. Otherwise, the user will only be granted the access permission if they have the role.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


