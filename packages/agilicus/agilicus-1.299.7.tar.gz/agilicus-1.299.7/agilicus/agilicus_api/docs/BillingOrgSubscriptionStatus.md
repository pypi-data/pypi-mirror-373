# BillingOrgSubscriptionStatus

Object describing the status of a Billing Account Subscription

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**orgs** | [**[Organisation]**](Organisation.md) | the list of organisations that are connected to this billing subscription  | [optional] 
**subscription** | [**BillingSubscription**](BillingSubscription.md) |  | [optional] 
**balance** | [**BillingOrgSubscriptionBalance**](BillingOrgSubscriptionBalance.md) |  | [optional] 
**feature_overrides** | [**[Feature]**](Feature.md) | feature overrides specifically associated with this subscription | [optional] 
**usage_metrics** | [**UsageMetrics**](UsageMetrics.md) |  | [optional] 
**products** | [**[BillingProduct]**](BillingProduct.md) | The provider products associated with this billing account.  | [optional] 
**product** | [**Product**](Product.md) |  | [optional] 
**provider_status** | [**BillingProviderSubscriptionStatus**](BillingProviderSubscriptionStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


