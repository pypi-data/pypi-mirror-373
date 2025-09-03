# BillingCustomer

A billable customer assigned to one or more organisations.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier for the object. | [optional] 
**name** | **str** | The customer&#39;s full name or business name. | [optional] 
**email** | **str** | The customer&#39;s email address | [optional] 
**balance** | **int** | The current balance, if any, that’s stored on the customer. If negative, the customer has credit to apply to their next invoice. If positive, the customer has an amount owed that’s added to their next invoice. The balance only considers amounts that Stripe hasn’t successfully applied to any invoice. It doesn’t reflect unpaid invoices. This balance is only taken into account after invoices finalize.  | [optional] 
**created** | **int** | Time at which the object was created. Measured in seconds since the Unix epoch. | [optional] 
**currency** | **str, none_type** | Three-letter [ISO code for the currency](https://stripe.com/docs/currencies) the customer can be charged in for recurring billing purposes. | [optional] 
**description** | **str, none_type** | An arbitrary string attached to the object. Often useful for displaying to users. | [optional] 
**invoice_prefix** | **str, none_type** | The prefix for the customer used to generate unique invoice numbers. | [optional] 
**livemode** | **bool** | Has the value &#x60;true&#x60; if the object exists in live mode or the value &#x60;false&#x60; if the object exists in test mode. | [optional] 
**metadata** | **{str: (str,)}** | Set of [key-value pairs](https://stripe.com/docs/api/metadata) that you can attach to an object. This can be useful for storing additional information about the object in a structured format. | [optional] 
**phone** | **str, none_type** | The customer&#39;s phone number. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


