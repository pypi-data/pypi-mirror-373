# HTTPSummaryStats

summary statistics for HTTP requests made to a server 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**http_bytes_received** | **int** | The number of bytes, including headers, received from the server | [optional] 
**http_bytes_sent** | **int** | The number of bytes, including headers, sent to the server | [optional] 
**requests_started** | **int** | The total number of requests started | [optional] 
**requests_finished** | **int** | The total number of requests finished | [optional] 
**requests_status_1xx** | **int** | The number of requests which completed with a status code between 100 and 199  | [optional] 
**requests_status_2xx** | **int** | The number of requests which completed with a status code between 200 and 299  | [optional] 
**requests_status_3xx** | **int** | The number of requests which completed with a status code between 300 and 399  | [optional] 
**requests_status_4xx** | **int** | The number of requests which completed with a status code between 400 and 499  | [optional] 
**requests_status_5xx** | **int** | The number of requests which completed with a status code between 500 and 599  | [optional] 
**requests_status_unknown** | **int** | The number of requests which completed with an unknown status code  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


