# BillingOrgSubscriptionSpec

Object describing the spec of a Billing Org Subscription. Links to a license by license_id. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_account_id** | **str** | the billing_account_id associated with this subscription | 
**dev_mode** | **bool** | Billing subscription is in dev mode, used for connecting to non-live backend billing API.  | [optional] 
**subscription_id** | **str, none_type** | The subscription_id associated with this BillingAccountSubscription | [optional] 
**usage_override** | [**[BillingSubscriptionUsageOverrideItem], none_type**](BillingSubscriptionUsageOverrideItem.md) | Override to billing-usage job, including minimum-commit.  | [optional] 
**feature_overrides** | **[str], none_type** | a list of features to apply to this org subscription | [optional] 
**product_id** | **str** | The Product this BillingOrgSubscription is associated with. | [optional] 
**cancel_detail** | [**BillingSubscriptionCancelDetail**](BillingSubscriptionCancelDetail.md) |  | [optional] 
**license_id** | **str** | Unique identifier | [optional] 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | Overrides for constraints applied to this license. Only use in exceptional circumstances.  | [optional] 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


