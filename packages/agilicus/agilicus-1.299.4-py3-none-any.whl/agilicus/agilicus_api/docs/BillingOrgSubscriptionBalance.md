# BillingOrgSubscriptionBalance

Object describing the subscription balance

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**upcoming_invoice** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | A Billing Upcoming Invoice object. | [optional] 
**subscription_balance** | **int** | The current subscription balance (in cents)  | [optional] 
**estimate_balance_end_date** | **datetime** | An estimate of the date when the subscription_balance will be consumed. This estimate is based upon the upcoming_invoice.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


