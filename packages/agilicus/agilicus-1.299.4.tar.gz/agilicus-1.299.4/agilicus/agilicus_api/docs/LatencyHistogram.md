# LatencyHistogram

A latency histogram. Contains a list of buckets + a final tail bucket. Each bucket describe what part of the histogram it measures. The tail bucket captures all items which would otherwise fall outside the range of the buckets. A histogram with only a tail_bucket is essentially a counter. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**buckets** | [**[LatencyHistogramBuckets]**](LatencyHistogramBuckets.md) | The buckets composing the histogram | 
**tail_bucket** | **int** | The total number of times something was measured by the histogram. This serves as the long tail of the histogram, but also as a total counter for the number of events measured.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


