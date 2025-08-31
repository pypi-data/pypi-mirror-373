# ListSessionsResponse

Response object for the list of sessions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sessions** | [**[Session]**](Session.md) | The matching Session objects | 
**limit** | **int** | Limit on the number of rows in the response | 
**previous_created_time** | **datetime** | The earliest created time on the current page. A value of \&quot;\&quot; is the start of the first page. This is typically combined with other pagination parameters to sub-paginate data that has too many results for the primary pagination key.  | [optional] [readonly] 
**page_at_created_time** | **datetime** | The earliest created time on the next page. This is typically combined with other pagination parameters to sub-paginate data that has too many results for the primary pagination key.  | [optional] [readonly] 
**previous_user_id** | **str** | The first user_id on the current page. A value of \&quot;\&quot; is the start of the first page. | [optional] 
**page_at_user_id** | **str** | The user_id to page at. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


