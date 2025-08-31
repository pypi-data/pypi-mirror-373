# APIKeyIntrospect

An API Key to introspection, along with some options to control how to process the results. In order to introspect an API Key you need both the secret representing the API Key as well as the email address of the user who issued the secret key. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_key_auth_info** | [**APIKeyIntrospectAuthorizationInfo**](APIKeyIntrospectAuthorizationInfo.md) |  | 
**introspect_options** | [**TokenIntrospectOptions**](TokenIntrospectOptions.md) |  | [optional] 
**multi_org** | **bool** | Whether or not to allow this APIKey to represent multiple orgs | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


