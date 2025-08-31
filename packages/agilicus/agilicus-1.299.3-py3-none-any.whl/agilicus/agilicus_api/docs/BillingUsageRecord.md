# BillingUsageRecord

A billing usage record

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dry_run** | **bool** | When true, the actual usage record is not written to the backend billing database. This is useful to determine what the resulting record would be written as.  | [optional]  if omitted the server will use the default value of False
**quantity** | **int** | Total usage quantity for the specified date.  This field is readOnly and is automatically determined by the backend server before applying. Its result is returned back in the response.  | [optional] [readonly] 
**timestamp** | **int** | The timestamp when this usage occurred.  This field is readOnly and is automatically determined by the backend server before applying. Its result is returned back in the response.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


