# NetworkSummaryStats

Stats summarising the operations performed by an application service. The meaning of the stats depends on the type of application service:  - a share: share requests  - otherwise: connections (e.g. tcp) 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bytes_received** | **int** | The number of bytes received from the server | 
**bytes_sent** | **int** | The number of bytes, sent to the server | 
**connections_total** | **int** | The total number of connection established, finished or failed | 
**connections_successful** | **int** | The total number of connections which successfully established. This includes current connections  | 
**connections_failed** | **int** | The total number of times a connection attempt failed. This aggregates the detailed connection failure conditions  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


