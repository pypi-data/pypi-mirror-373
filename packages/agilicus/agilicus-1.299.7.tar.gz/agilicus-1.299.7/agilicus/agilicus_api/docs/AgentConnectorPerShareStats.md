# AgentConnectorPerShareStats

Statistics related to an individual share.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**share_prefix** | **str** | The prefix used to route the requests to the shared local path. This is typically derived from the share_name of the Share.  | 
**share_id** | **str** | The unique ID of the FileShareService to which this share corresponds.  | 
**local_path** | **str** | The path on the local file system which is being shared. | 
**total_requests** | **int** | The total number of requests made to this share. | 
**successful_requests** | **int** | The total number of requests which have succeeded. | 
**failed_requests** | **int** | The total number of requests which have failed. | 
**bytes_sent** | **int** | The total number of bytes sent in the body of responses to requests. This includes any metadata about files, or data included in failure responses.  | 
**bytes_received** | **int** | The total number of bytes received in the body of requests. This includes any metadata about files, files themselves, or general commands such as lock requests.  | 
**share_start_time** | **datetime** | When the share was started. | 
**correct_share_permissions** | **bool** | True if share has correct permissions, false otherwise.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


