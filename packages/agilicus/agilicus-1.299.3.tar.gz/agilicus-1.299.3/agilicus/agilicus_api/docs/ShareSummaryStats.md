# ShareSummaryStats

Summary statistics for requests made to a share. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests_total** | **int** | The total number of requests to the share  | [optional] 
**requests_successful** | **int** | The total number of requests where the share functioned as expected. Note that this includes requests which may appear as failures from the perspective of the end user. For example, a request for a non-existant file may seem to be a failure. However, it counts as a succesful request here because the share protocol is operating as designed.  | [optional] 
**requests_failed** | **int** | The total number of requests where the share did not function as expected. Note that this does not includes requests which may appear as failures from the perspective of the end user. For example, a request for a non-existant file may seem to be a failure. However, it does not count as a failed request here because the share protocol is operating as designed.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


