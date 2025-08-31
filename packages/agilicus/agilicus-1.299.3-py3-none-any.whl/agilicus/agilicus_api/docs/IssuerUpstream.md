# IssuerUpstream

A summary of the issuer upstreams

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**issuer_id** | **str** | Unique identifier | [readonly] 
**org_id** | **str** | ID of the organisation which owns the issuer | 
**name** | **str** | A name used to uniquely refer to the upstream identity provider configuration. This is the text that will be displayed when presenting the upstream identity for login. | 
**upstream_issuer** | **str** | The upstream issuer uri. This is the URI which identifies the issuer against which users selecting this upstream will authenticate. | 
**upstream_type** | **str** | The type of upstream. For instance an OpenID Connector Upstream. | [optional] 
**admin_status** | [**AdminStatus**](AdminStatus.md) |  | [optional] 
**trap_disabled** | **bool** | Inidicates whether traps (notifications) should be disabled for this entity. A true state indicates notifications will not be sent on transition.  | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


