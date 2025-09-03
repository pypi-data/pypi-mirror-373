# OIDCUpstreamIdentityProvider

Custom OIDC Upstream Identity Provider

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A name used to uniquely refer to the upstream identity provider configuration. This is the text that will be displayed when presenting the upstream identity for login. | 
**issuer** | **str** | The upstream issuer uri. This is the URI which identifies the issuer against which users selecting this OIDCUpstreamIdentityProvider will authenticate. The issuer must support the OpenID Connect discovery document described here: https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig. | 
**client_id** | **str** | The client ID for the upstream identity provider | 
**icon** | **str** | The icon file to be used, limited to: numbers, letters, underscores, hyphens and periods. It is part of a css class (with the periods replaced by underscores).  To use a custom icon than the provided default you will need to add the icon the static/img folder and update the static css file to add a new css button like below &#x60;&#x60;&#x60;json .dex-btn-icon--&lt;your-logo_svg&gt; {   background-image: url(../static/img/&lt;your-logo.svg&gt;); } &#x60;&#x60;&#x60;  To use a default icon simply enter an icon name from the pre-provided defaults found in the static/img folder The default icons are   - bitbucket   - coreos   - email   - github   - gitlab   - google   - ldap   - linkedin   - microsoft   - oidc   - saml  | [optional] 
**client_secret** | **str** | The secret presented to the upstream during any workflows which require authentication | [optional] 
**issuer_external_host** | **str** | A proxy standing in for the main issuer host. Use this if fronting the upstream through the Agilicus infrastructure | [optional] 
**username_key** | **str** | Allows changing the key in the OIDC response claims used to determine the full name of the user. If not present, defaults to the standard name | [optional] 
**email_key** | **str** | Allows changing the key in the OIDC response claims used to determine the email address of the user. If not present, defaults to the standard email | [optional] 
**email_verification_required** | **bool** | Controls whether email verification is required for this OIDC provider. Some OIDC providers do not take steps to verify the email address of users, or may not do so in all cases. Setting this value to true will reject any successful upstream logins for users which have not had their email address verified. | [optional]  if omitted the server will use the default value of True
**request_user_info** | **bool** | Controls whether the system will retrieve extra information about the user from the provider&#39;s user_info endpoint. This can be useful if the initial OIDC response does not contain sufficient information to determine the email address or user&#39;s name. Setting this value to true will cause extra requests to be generated to the upstream every time a user logs in to it. | [optional] 
**user_id_key** | **str** | Changes the key used to determine the id of the user in this upstream. The key will be used to retrieve the user id from the id token claims returned from the upstream when the user logs in. This user id is in turn used to link the user to its identity within the system. If not present, the system will fall back on the default, which is &#x60;sub&#x60;.  | [optional] 
**auto_create_status** | [**AutoCreateStatus**](AutoCreateStatus.md) |  | [optional] 
**prompt_mode** | **str** | Controls how the issuer sets the &#39;prompt&#39; field of the request to the upstream identity provider. It can take the following values: - &#x60;auto&#x60;: Determine whether to set the prompt field based on other criteria of the request, such as whether offline   mode is requested. - &#x60;disabled&#x60;: Never set the prompt field.  | [optional] 
**oidc_flavor** | **str** | Controls the type/flavor of the upstream OIDC provider. Some providers have specific functionality that differs from standard oidc. For example, Microsoft utilizes the Graph API for group management. For example, if the upstream issuer is microsoft, setting this flavor to microsoft will query the groups by name so that Agilicus will reconcile all groups by the name, rather than its guid.  | [optional]  if omitted the server will use the default value of "oidc"
**client_authorization_type** | **str, none_type** | supports values:   &#39;&#39; or null/not set: client_secret authorization is used   &#39;federated-credential&#39;: Supports Microsoft federated credential.     In side the Microsoft Application Registration,     in \&quot;Certificates &amp; Secrets\&quot; section, choose &#39;Federated credentials&#39;. Choose \&quot;Other Issuer\&quot;, and specify     the URL of the issuer (ie. https://auth.&lt;org domain&gt;). Choose Explicit subject identifier, and enter     the client ID of the Microsoft Application.  | [optional] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


