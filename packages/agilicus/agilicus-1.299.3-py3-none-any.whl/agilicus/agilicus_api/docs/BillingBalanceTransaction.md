# BillingBalanceTransaction

Customer Balance transactions represent funds moving through your Stripe account. Stripe creates them for every type of transaction that enters or leaves your Stripe account balance. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **int** | Gross amount of this transaction (in cents). A positive value represents funds applied to this subscription. A negative value represents funds removed from this transaction.  | [optional] 
**description** | **str** | An arbitrary string attached to the object. Often useful for displaying to users.  | [optional] 
**currency** | **str** | The currency type for the amount property.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


