# RegionSpec

The RegionSpec describes the properties of a Region. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | region name | 
**routing** | [**RegionRouting**](RegionRouting.md) |  | 
**master_pop_id** | **str** | Designates a particular PointOfPresence as a master.  This property is normally not required when there is a single PointOfPresence specified in pop_ids.  This guid must also exist inside pop_ids.  | [optional] 
**pop_ids** | **[str]** | the configured pop ids that are associated to this Region  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


