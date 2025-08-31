# ListInboxItemsResponse

The result of querying the items in an inbox. To understand how many items there are without retrieving them, pass a limit of 0 to the query. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**inbox_items** | [**[InboxItem]**](InboxItem.md) | The items corresponding to the query | 
**summary** | [**ListInboxItemsSummary**](ListInboxItemsSummary.md) |  | 
**limit** | **int** | Limit on the number of rows in the response | [optional] 
**page_at_received_date** | **datetime** | The received date in the pagination query to get the next page. | [optional] 
**page_at_id** | **str** | The inbox item id to use in the pagination query to get the next page. Useful in case more than one message was received on the same date.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


