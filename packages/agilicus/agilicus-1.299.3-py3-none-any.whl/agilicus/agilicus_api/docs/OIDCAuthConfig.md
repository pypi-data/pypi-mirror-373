# OIDCAuthConfig

The OIDC configuration for authentication with OIDC connector.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auth_enabled** | **bool** | Whether the authentication is enabled. If true, users will be forced to log in before accessing any of its assets. If false, no authentication will be performed.  | 
**client_id** | **str** | The OIDC client identifier to use when logging in with this application. | 
**issuer** | **str** | The url of the OpenID Connect issuer. | 
**logout_url** | **str** | The relative http path to the logout page. | [optional] 
**scopes** | [**[OIDCProxyScope]**](OIDCProxyScope.md) | A list of scopes to be requested on behalf of the user of the application. | [optional] 
**path_config** | [**OIDCAuthPathConfig**](OIDCAuthPathConfig.md) |  | [optional] 
**redirect_after_signin_path** | **str** | The path to which the user will be redirected on successful signin.  If this is not set, the default is &#39;/&#39;.  | [optional] 
**redirect_subpath** | **str** | The subpath to redirect if application is set in a subdirectory (not root).  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


