# ShareDetailedStats

Detailed statistics for requests made to a share. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests_read** | **int** | The number of requests which read a file or directory.  | [optional] 
**requests_create** | **int** | The number of requests which created a file or directory  | [optional] 
**requests_modify** | **int** | The number of requests which modified a file or directory  | [optional] 
**requests_delete** | **int** | The number of requests which deleted a file or directory  | [optional] 
**requests_lock** | **int** | The number of requests which locked a file or directory  | [optional] 
**requests_other** | **int** | The number of requests which performed an operation not broken out in to a specific counter  | [optional] 
**failure_not_found** | **int** | The number of requests which failed because the connector could not find the share  | [optional] 
**failure_permission** | **int** | The number of requests which failed because the connector did not have permission to access the share  | [optional] 
**failure_other** | **int** | The number of requests which failed for an unspecified reason.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


