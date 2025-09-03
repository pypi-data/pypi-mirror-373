# BillingProviderSubscriptionStatus

Provides details of the backend provider subscription and interactions with Agilicus Product, including reconcile detail to determine differences between the subscription current prices and the configured product prices. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_subscription_match** | **bool** | This provides a simple boolean, which identifies if the product_id and its associated price_ids, are configured and used inside the backend provider subscription.  A value of True says they match, otherwise a value of False says they do not match. When false, the subscription_missing_prices and subscription_additional_prices can provide info as to which price ids are mismatched.  | [optional] 
**subscription_missing_prices** | [**[BillingProductPrice]**](BillingProductPrice.md) | A list of billing product price ids that are present in the product, but are not in the current subscription.  | [optional] 
**subscription_additional_prices** | [**[BillingProductPrice]**](BillingProductPrice.md) | A list of billing product price ids that are not present in the product, but are in the current subscription.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


