# ProductSpec

The specification for a Product.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The product&#39;s name, meant to be displayable to the customer. | 
**description** | **str** | The product&#39;s detailed description. | [optional] 
**dev_mode** | **bool** | Product is in dev mode, used for connecting to non-live backend billing API.  | [optional] 
**label** | **str** | A unique short name for this product. This is used to query for a product with a specific label.  | [optional] 
**billing_product_prices** | [**[BillingProductPrice]**](BillingProductPrice.md) | A list of billing product price ids that are contained in this Product | [optional] 
**trial_period** | **int, none_type** | Product trial period (days)  | [optional] 
**features** | **[str], none_type** | A list of product features by guid associated with this product.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


