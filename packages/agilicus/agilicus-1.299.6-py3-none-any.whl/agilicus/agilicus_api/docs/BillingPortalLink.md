# BillingPortalLink

Represents a temporary, one-time-use link to the billing system's self-serve portal. Creating a link object will provision a one-time-use link in the billing system so that a user may manage their contact info, subscriptions, billing info and so on. The link will expire after some period of time. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**return_uri** | **str** | The page to return to after the user has finished their configuration. The self-serve portal will present this link to the user so that they may return when they have finished. This should be a fully-qualified domain. Typically you&#39;ll place the URI of the page the user was at prior to navigating to &#x60;portal_uri&#x60;.  | 
**portal_uri** | **str** | The URI to send the user to so that they may configure their billing account. This URI will eventually expire. This is a sensitive value: do not store it, or transmit it anywhere.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


