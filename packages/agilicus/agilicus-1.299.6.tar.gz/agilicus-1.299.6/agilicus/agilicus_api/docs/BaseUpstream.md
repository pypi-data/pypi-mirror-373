# BaseUpstream

Base class of an upstream. This represents the common pieces of information for an upsteam.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A name used to uniquely refer to the upstream identity provider configuration. This is the text that will be displayed when presenting the upstream identity for login. | [optional] 
**issuer** | **str** | The upstream issuer uri. This is the URI which identifies the issuer against which users selecting this upstream will authenticate. | [optional] 
**upstream_type** | **str** | The type of upstream. For instance an OpenID Connector Upstream. | [optional] 
**icon** | **str** | The icon file to be used, limited to: numbers, letters, underscores, hyphens and periods. It is part of a css class (with the periods replaced by underscores).  To use a custom icon than the provided default you will need to add the icon the static/img folder and update the static css file to add a new css button like below &#x60;&#x60;&#x60;json .dex-btn-icon--&lt;your-logo_svg&gt; {   background-image: url(../static/img/&lt;your-logo.svg&gt;); } &#x60;&#x60;&#x60;  To use a default icon simply enter an icon name from the pre-provided defaults found in the static/img folder The default icons are   - bitbucket   - coreos   - email   - github   - gitlab   - google   - ldap   - linkedin   - microsoft   - oidc   - saml  | [optional] 
**auto_create_status** | [**AutoCreateStatus**](AutoCreateStatus.md) |  | [optional] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


