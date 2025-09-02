# ListBillingAccountsResponse

Response object for billing accounts query

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **int** | Limit on the number of rows in the response | 
**billing_accounts** | [**[BillingAccount]**](BillingAccount.md) | List of billing accounts | [optional] 
**page_at_id** | **str** | The id to request in the pagination query to get the next page. | [optional] 
**previous_id** | **str** | The next page to fetch when searching backwards. If an empty string, the current page is the first page.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


