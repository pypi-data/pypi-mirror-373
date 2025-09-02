# UsageMetric

A usage metrics for a given resource. A metric contains one or more measurements Provisioned measurements pertain to the set of created resources in the org specified by org_id Active metrics is the set of resources currently deemed active. Each resource has a different algorithm for determining if the usage metric is active or not.  A usage metric can be associated to a single org_id, or a list of org_ids. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The type of the Usage | [optional] 
**org_id** | **str** | The unique id of the Organisation to which this record applies.  | [optional] 
**org_ids** | **[str]** | The list of orgs to which this record applies. | [optional] 
**provisioned** | [**UsageMeasurement**](UsageMeasurement.md) |  | [optional] 
**active** | [**UsageMeasurement**](UsageMeasurement.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


