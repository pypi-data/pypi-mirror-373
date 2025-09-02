# BillingSubscriptionCancelDetail

Object describing billing a billing subscription cancelation detail.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancel_at_period_end** | **bool** | The subscription associated with this organisation will cancelled at the subscription period end. This organisation and its suborgs will be disabled at approximately that time.  Only one of cancel_at_period_end, cancel_at or immediately can be utilized.  | [optional] 
**cancel_at** | **datetime** | The subscription associated with this organisation will cancelled at the the specified date-time. This organisation and its suborgs will be disabled at approximately that time.  Only one of cancel_at_period_end, cancel_at or immediately can be utilized.  | [optional] 
**immediately** | **bool** | The subscription associated with this organisation will cancelled immediately. This organisation and its suborgs will be disabled.  Only one of cancel_at_period_end, cancel_at or immediately can be utilized.  | [optional] 
**comment** | **str** | Additional comments about why the user canceled the subscription, if the subscription was canceled explicitly by the user.  | [optional] 
**feedback** | **str** | The customer submitted reason for why they canceled, if the subscription was canceled explicitly by the user. Possible values   - customer_service - Customer service was less than expected   - low_quality - Quality was less than expected   - missing_features - Some features are missing   - other - other reason   - switched_service - I’m switching to a different service   - too_complex - Ease of use was less than expected   - too_expensive - It’s too expensive   - unused - I don’t use the service enough  | [optional] 
**subscription** | [**BillingSubscription**](BillingSubscription.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


