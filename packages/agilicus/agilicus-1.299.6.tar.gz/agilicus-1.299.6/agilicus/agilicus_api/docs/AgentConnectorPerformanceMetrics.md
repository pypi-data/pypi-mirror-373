# AgentConnectorPerformanceMetrics

Performance Metrics for connector instance. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | [**ConnectorStatsMetadata**](ConnectorStatsMetadata.md) |  | [optional] 
**cpu_total_seconds** | **float** | Estimated total available CPU time for user Go code or the Go runtime, as defined by GOMAXPROCS. In other words, GOMAXPROCS integrated over the wall-clock duration this process has been executing for. This metric is an overestimate, and not directly comparable to system CPU time measurements. Compare only with other /cpu/classes metrics. Sum of all metrics in /cpu/classes.  | [optional] 
**cpu_user_seconds** | **float** | Estimated total available CPU time for user Go code or the Go runtime, as defined by GOMAXPROCS. In other words, GOMAXPROCS integrated over the wall-clock duration this process has been executing for. This metric is an overestimate, and not directly comparable to system CPU time measurements. Compare only with other /cpu/classes metrics. Sum of all metrics in /cpu/classes.  | [optional] 
**memory_heap_free** | **int** | Memory that is completely free and eligible to be returned to the underlying system, but has not been. This metric is the runtime&#39;s estimate of free address space that is backed by physical memory.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


