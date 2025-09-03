# Issuer

Object describing the properties of an issuer. Issuers support an inheritence hierachy. By setting parent_issuer to the guid of another issuer, the issuer will inherit some properties of that issuer. Setting it to null or leaving it undefined. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issuer** | **str** | connect id issuer | 
**id** | **str** | Unique identifier | [optional] [readonly] 
**enabled** | **bool** | Describes whether or not the issuer is enabled | [optional]  if omitted the server will use the default value of True
**org_id** | **str** | ID of the organisation which owns the issuer | [optional] 
**theme_file_id** | **str** | ID of the theme file. The theme file is a zip file containing the web assets to show the client on login. | [optional] 
**upstream_redirect_uri** | **str** | Upstream redirect URI is the URI to which OpenID Connect upstreams will redirect after authentication. This is provisioned by Agilicus, but must be allowed by the upstream. | [optional] 
**managed_upstreams** | [**[ManagedUpstreamIdentityProvider]**](ManagedUpstreamIdentityProvider.md) | The set of managed upstream identity providers for this issuer. A managed upstream has its configuration managed by default, and can be enabled or disabled for this issuer via this api. | [optional] 
**oidc_upstreams** | [**[OIDCUpstreamIdentityProvider]**](OIDCUpstreamIdentityProvider.md) | The set of OpenID Connect upstream identity providers configured for this issuer. An upstream is managed by the client, and can be configured for this issuer via this api. | [optional] 
**local_auth_upstreams** | [**[LocalAuthUpstreamIdentityProvider]**](LocalAuthUpstreamIdentityProvider.md) | The set of local authentication upstream identity providers configured for this issuer. A local authentication upstream can be an onsite Agilicus Agent. | [optional] 
**application_upstreams** | [**[ApplicationUpstreamIdentityProvider]**](ApplicationUpstreamIdentityProvider.md) | The set of application upstream identity providers configured for this issuer. Applications that can act as their own source of identity can be used as application upstreams.  | [optional] 
**kerberos_upstreams** | [**[KerberosUpstreamIdentityProvider]**](KerberosUpstreamIdentityProvider.md) | The set of kerberos upstream identity providers for this issuer. Device identity can be used to enable zero-interaction login for users on trusted devices which have already entered their credentials.  | [optional] 
**clients** | [**[IssuerClient]**](IssuerClient.md) | List of clients | [optional] [readonly] 
**upstream_group_mappings** | [**[UpstreamGroupMapping]**](UpstreamGroupMapping.md) | List of upstream group mappings | [optional] [readonly] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**saml_state_encryption_key** | **str** | The encryption key used to secure the saml state. This is used to encrypt the saml cookie that is used to identify the user.  | [optional] 
**service_account_id** | **str** | Service account GUID used for the issuer | [optional] [readonly] 
**service_account_user_id** | **str** | Service account user GUID used for the issuer | [optional] [readonly] 
**verified_domains** | **[str]** | The list of verified domains for the issuer. This is used to authorize users with multiple upstream identities but who are represented as a single user in the Agilicus System. For example agilicus.com would allow users whose email ended in @agilicus.com to login from multiple upstream identity providers.  | [optional] [readonly] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**parent_issuer** | **str, none_type** | A unique identifier which can be empty. The meaning of it being empty depends on the context in which it is used, but usually it implies that something is not set.  | [optional] 
**status** | [**IssuerStatus**](IssuerStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


